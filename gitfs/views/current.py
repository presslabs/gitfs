import re
import os
import errno

from fuse import FuseOSError

from gitfs.worker.decorators import while_not

from .passthrough import PassthroughView, STATS


class CurrentView(PassthroughView):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.dirty = {}
        self.dirties = 0

    @while_not("read_only")
    @while_not("merging")
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

    def symlink(self, name, target):
        result = os.symlink(target, self._full_path(name))

        message = "Create symlink to %s for %s" % (target, name)
        self.queue(add=name, message=message)

        return result

    def readlink(self, path):
        return os.readlink(self._full_path(path))

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
    @while_not("merging")
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
                self.dirties -= 1
                self.dirty[path]['is_dirty'] = False
                # delete it
                self.dirty[path]['delete_it'] = True

                if self.dirties > 0:
                    self.somebody_is_writing.set()
                else:
                    self.somebody_is_writing.clear()

            raise FuseOSError(errno.EFBIG)

        result = super(CurrentView, self).write(path, buf, offset, fh)
        self.dirty[path] = {
            'message': 'Update %s' % path,
            'is_dirty': True,
            'size': size
        }
        self.dirties += 1

        return result

    @while_not("read_only")
    @while_not("merging")
    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        path = "%s/.keep" % os.path.split(path)[1]
        if not os.path.exists(path):
            fh = self.create(path, 0644)
            self.release(path, fh)

        return result

    @while_not("read_only")
    @while_not("merging")
    def create(self, path, mode, fi=None):
        result = super(CurrentView, self).create(path, mode, fi)
        self.dirty[path] = {
            'message': "Created %s" % path,
            'is_dirty': True,
            'size': 0,
        }
        self.dirties += 1

        return result

    @while_not("read_only")
    @while_not("merging")
    def chmod(self, path, mode):
        """
        Executes chmod on the file at os level and then it commits the change.
        """

        result = super(CurrentView, self).chmod(path, mode)

        message = 'Chmod to %s on %s' % (str(oct(mode))[3:-1], path)
        self._index(add=path, message=message)

        return result

    @while_not("read_only")
    @while_not("merging")
    def fsync(self, path, fdatasync, fh):
        """
        Each time you fsync, a new commit and push are made
        """
        result = super(CurrentView, self).fsync(path, fdatasync, fh)

        message = 'Fsync %s' % path
        self._index(add=path, message=message)

        return result

    @while_not("read_only")
    @while_not("merging")
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
                self.dirties -= 1
                self.dirty[path]['is_dirty'] = False
                self._index(add=path, message=self.dirty[path]['message'])

        if self.dirties > 0:
            self.somebody_is_writing.set()
        else:
            self.somebody_is_writing.clear()

        return os.close(fh)

    @while_not("read_only")
    @while_not("merging")
    def unlink(self, path):
        result = super(CurrentView, self).unlink(path)

        message = 'Deleted %s' % path
        self._index(remove=path, message=message)

        return result

    def _index(self, message, add=None, remove=None):
        add = self._sanitize(add)
        remove = self._sanitize(remove)

        if remove is not None:
            self.repo.index.remove(self._sanitize(remove))

        if add is not None:
            self.repo.index.add(self._sanitize(add))

        self.queue(add=add, remove=remove, message=message)

    def _sanitize(self, path):
        if path is not None and path.startswith("/"):
            path = path[1:]
        return path
