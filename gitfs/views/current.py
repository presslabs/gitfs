import re
import os
import time
import errno

from fuse import FuseOSError

from gitfs.utils.decorators.while_not import while_not
from gitfs.utils.decorators.not_in import not_in

from .passthrough import PassthroughView, STATS


class CurrentView(PassthroughView):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.dirty = {}
        self.writing = set([])

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["old", "new"])
    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        result = super(CurrentView, self).rename(old, new)

        message = "Rename %s to %s" % (old, new)
        self._index(**{
            'remove': os.path.split(old)[1],
            'add': new,
            'message': message
        })

        return result

    @while_not("want_to_merge")
    def symlink(self, name, target):
        result = os.symlink(target, self._full_path(name))

        message = "Create symlink to %s for %s" % (target, name)
        self._index(add=name, message=message)

        return result

    @not_in("ignore", check=["path"])
    def readlink(self, path):
        return os.readlink(self._full_path(path))

    @not_in("ignore", check=["path"])
    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)

        attrs = dict((key, getattr(st, key)) for key in STATS)
        attrs.update({
            'st_uid': self.uid,
            'st_gid': self.gid,
        })

        return attrs

    @while_not("read_only")
    @not_in("ignore", check=["path"])
    def write(self, path, buf, offset, fh):
        """
            We don't like big big files, so we need to be really carefull
            with them. First we check for offset, then for size. If any of this
            is off limit, raise EFBIG error and delete the file.
        """

        size = len(buf)
        if path in self.dirty:
            size += self.dirty[path]['size']

        if size > self.max_size or offset > self.max_offset:
            if path in self.dirty:
                # mark it as not dirty
                self.dirty[path]['is_dirty'] = False
                # delete it
                self.dirty[path]['delete_it'] = True

            raise FuseOSError(errno.EFBIG)

        result = super(CurrentView, self).write(path, buf, offset, fh)
        self.dirty[path] = {
            'message': 'Update %s' % path,
            'is_dirty': True,
            'size': size
        }

        return result

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["path"])
    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        path = "%s/.keep" % os.path.split(path)[1]
        if not os.path.exists(path):
            fh = self.create(path, 0644)
            self.release(path, fh)

        return result

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["path"])
    def create(self, path, mode, fi=None):
        self.somebody_is_writing.set()
        result = super(CurrentView, self).create(path, mode, fi)
        self.dirty[path] = {
            'message': "Created %s" % path,
            'is_dirty': True,
            'size': 0,
        }
        self.somebody_is_writing.clear()
        return result

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["path"])
    def chmod(self, path, mode):
        """
        Executes chmod on the file at os level and then it commits the change.
        """

        result = super(CurrentView, self).chmod(path, mode)

        print "CHMOOOOD"
        self.somebody_is_writing.set()
        message = 'Chmod to %s on %s' % (str(oct(mode))[3:-1], path)
        self._index(add=path, message=message)
        self.somebody_is_writing.clear()

        return result

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["path"])
    def fsync(self, path, fdatasync, fh):
        """
        Each time you fsync, a new commit and push are made
        """

        self.somebody_is_writing.set()
        result = super(CurrentView, self).fsync(path, fdatasync, fh)

        message = 'Fsync %s' % path
        self._index(add=path, message=message)

        self.somebody_is_writing.clear()

        return result

    @not_in("ignore", check=["path"])
    def open(self, path, flags):
        write_mode = flags & (os.O_WRONLY | os.O_RDWR |
                              os.O_APPEND | os.O_CREAT)

        if self.want_to_merge.is_set() and write_mode:
            print "want to write"
            while self.want_to_merge.is_set():
                time.sleep(2)

        full_path = self._full_path(path)
        fh = os.open(full_path, flags)

        if write_mode:
            self.writing.add(fh)

        return fh

    @while_not("read_only")
    @not_in("ignore", check=["path"])
    def release(self, path, fh):
        """
        Check for path if something was written to. If so, commit and push
        the changed to upstream.
        """

        if path in self.dirty:
            if ('delete_it' in self.dirty[path] and
               self.dirty[path]['delete_it']):
                # delete the file
                super(CurrentView, self).unlink(os.path.split(path)[1])
                self.dirty[path]['delete_it'] = False

            if self.dirty[path]['is_dirty']:
                self.dirty[path]['is_dirty'] = False
                self.somebody_is_writing.set()
                self._index(add=path, message=self.dirty[path]['message'])

        if fh in self.writing:
            self.writing.remove(fh)

        if not len(self.writing):
            self.somebody_is_writing.clear()
        else:
            self.somebody_is_writing.set()

        return os.close(fh)

    def readdir(self, path, fh):
        result = super(CurrentView, self).readdir(path, fh)
        return [entry for entry in result if entry not in self.ignore]

    @while_not("read_only")
    @while_not("want_to_merge")
    @not_in("ignore", check=["path"])
    def unlink(self, path):
        print path
        result = super(CurrentView, self).unlink(path)

        message = 'Deleted %s' % path
        self._index(remove=path, message=message)

        return result

    def _index(self, message, add=None, remove=None):
        non_empty = False

        add = self._sanitize(add)
        remove = self._sanitize(remove)

        if remove is not None:
            self.repo.index.remove(self._sanitize(remove))
            non_empty = True

        if add is not None:
            self.repo.index.add(self._sanitize(add))
            non_empty = True

        if non_empty:
            self.queue.commit(add=add, remove=remove, message=message)

    def _sanitize(self, path):
        if path is not None and path.startswith("/"):
            path = path[1:]
        return path
