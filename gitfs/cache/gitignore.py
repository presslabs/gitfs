# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import os
import fnmatch

from gitfs.cache.lru import lru_cache


class CachedIgnore(object):
    def __init__(self, ignore=False, submodules=False):
        self.items = []
        self.ignore = ".gitignore" if ignore else False
        self.submodules = ".gitmodules" if submodules else False
        self.cache = {}
        self.permanent = []

        self.update()

    def update(self):
        self.items = ['/.git', '.git/*', '/.git/*']

        if self.ignore and os.path.exists(self.ignore):
            with open(self.ignore) as gitignore:
                new_items = filter(lambda line: line != "",
                                   gitignore.read().split("\n"))

                self.items += new_items

        if self.submodules and os.path.exists(self.submodules):
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

        return fnmatch.fnmatch(key, item)
