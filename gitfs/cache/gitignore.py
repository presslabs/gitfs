import re
import os
import fnmatch

from gitfs.cache.lru import lru_cache


class CachedGitignore(object):
    def __init__(self, ignore=None, submodules=None):
        self.items = []
        self.ignore = ignore
        self.submodules = submodules
        self.cache = {}
        self.permanent = []

        self.update()

    def update(self):
        self.items = ['/.git', '.git/*', '/.git/*']

        if self.ignore is not None and os.path.exists(self.ignore):
            with open(self.ignore) as gitignore:
                new_items = gitignore.read().split("\n")
                if "" in new_items:
                    new_items.remove("")
                self.items += new_items

        if self.submodules is not None and os.path.exists(self.submodules):
            with open(self.submodules) as submodules:
                content = submodules.read()
                pattern = re.compile("path(\s*)=(\s*)(\w*)")
                results = re.findall(pattern, content)
                for result in results:
                    self.items.append("/%s/*" % result[2])
                    self.items.append("/%s" % result[2])
                    self.items.append("%s" % result[2])

        self.cache = {}

    def __contains__(self, path):
        return self.check_key(path)

    def check_key(self, key):
        for item in self.items:
            if self._check_item_and_key(item, key):
                return True
        return False

    @lru_cache(40000)
    def _check_item_and_key(self, item, key):
        if item == key:
            return True

        try:
            if fnmatch.fnmatch(key, item):
                return True
        except:
            pass

        return False
