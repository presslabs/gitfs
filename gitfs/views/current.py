import re
from .view import View
from log import log
from gitfs.filesystems.passthrough import PassthroughFuse


class CurrentView(View, PassthroughFuse):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path

    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        super(CurrentView, self).rename(old, new)
