import re
import os

from gitfs.filesystems.passthrough import PassthroughFuse, STATS

from .view import View


class CurrentView(View, PassthroughFuse):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path
        self.dirty = {}

    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        super(CurrentView, self).rename(old, new)

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

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
            'message': 'Update %s' % path
        }
        return result

    def release(self, path, fh):
        """
        Check for path if something was written to. If so, commit and push
        the changed to upstream.
        """

        # TODO:add them into a queue and commit/push them in another thread

        if path in self.dirty:
            clean_path = path
            if path.startswith("/"):
                clean_path = path[1:]

            self.repo.index.add(clean_path)
            # TODO: read commit message from dirty
            self.repo.commit(self.dirty[path]['message'], self.author,
                             self.commiter)
            self.repo.push("origin", self.branch)

            del self.dirty[path]

        return os.close(fh)

    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        # create .keep file
        path = "%s/.keep" % os.path.split(path)[1]
        fh = self.create(path, 0644)
        self.release(path, fh)

        return result

    def create(self, path, mode, fi=None):
        result = super(CurrentView, self).create(path, mode, fi)
        self.dirty[path] = {
            'message': "Created %s" % path
        }
        return result
