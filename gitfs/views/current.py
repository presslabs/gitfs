import re
import os

from gitfs.filesystems.passthrough import PassthroughFuse, STATS

from .view import View


class CurrentView(View, PassthroughFuse):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path

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

        print attrs
        return attrs
