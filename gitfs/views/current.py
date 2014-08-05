import re
import os

from gitfs.filesystems.passthrough import PassthroughFuse

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
        attr = super(CurrentView, self).getattr(path, fh)

        attr['st_uid'] = self.uid
        attr['st_gid'] = self.gid

        return attr
