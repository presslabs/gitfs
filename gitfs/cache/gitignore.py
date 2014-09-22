import os
import re

from gitfs.cache.lru import lru_cache


class CachedGitignore(object):
    def __init__(self, path=None):
        self.items = []
        self.path = path
        self.cache = {}

        self.update()

    def update(self):
        self.items = ['.git/', '/.git']

        if self.path is not None and os.path.exists(self.path):
            with open(self.path) as gitignore:
                new_items = gitignore.read().split("\n")
                if "" in new_items:
                    new_items.remove("")
                self.items += new_items

        self.cache = {}

    def __contains__(self, path):
        return self.check_key(path)

    def check_key(self, key):
        for item in self.items:
            if self._check_item_and_key(item, key):
                return True
        return False

    @lru_cache(4000)
    def _check_item_and_key(self, item, key):
        if item in key or item == key:
            return True

        item = re.compile(item)
        if item.search(key) is not None:
            return True

        return False
