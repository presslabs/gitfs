import re
import os

from gitfs.filesystems.passthrough import PassthroughFuse, STATS

from .view import View


class CurrentView(PassthroughFuse, View):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path
        self.dirty = {}

    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        super(CurrentView, self).rename(old, new)

        message = "Rename %s to %s" % (old, new)
        self.queue(**{
            'remove': os.path.split(old)[1],
            'add': new,
            'message': message
        })

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

    def write(self, path, buf, offset, fh):
        result = super(CurrentView, self).write(path, buf, offset, fh)
        self.dirty[path] = {
            'message': 'Update %s' % path,
            'is_dirty': True
        }
        return result

    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        path = "%s/.keep" % os.path.split(path)[1]
        if not os.path.exists(path):
            fh = self.create(path, 0644)
            self.release(path, fh)

        return result

    def create(self, path, mode, fi=None):
        result = super(CurrentView, self).create(path, mode, fi)
        self.dirty[path] = {
            'message': "Created %s" % path,
            'is_dirty': True
        }

        return result

    def chmod(self, path, mode):
        """
        Executes chmod on the file at os level and then it commits the change.
        """

        result = super(CurrentView, self).chmod(path, mode)

        message = 'Chmod to %s on %s' % (str(oct(mode))[3:-1], path)
        self.queue(add=path, message=message)

        return result

    def fsync(self, path, fdatasync, fh):
        """
        Each time you fsync, a new commit and push are made
        """
        result = super(CurrentView, self).fsync(path, fdatasync, fh)

        message = 'Fsync %s' % path
        self.queue(add=path, message=message)

        return result

    def release(self, path, fh):
        """
        Check for path if something was written to. If so, commit and push
        the changed to upstream.
        """

        if path in self.dirty and self.dirty[path]['is_dirty']:
            self.dirty[path]['is_dirty'] = False
            self.queue(add=path, message=self.dirty[path]['message'])

        return os.close(fh)
