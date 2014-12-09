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


class CachedIgnore(object):
    def __init__(self, ignore=False, submodules=False, exclude=False,
                 hard_ignore=None):
        self.items = []

        self.ignore = ignore
        self.submodules = submodules
        self.exclude = exclude

        self.cache = {}
        self.permanent = []
        self.hard_ignore = self._parse_hard_ignore(hard_ignore)

        self.update()

    def update(self):
        self.items = ['.git', '.git/*', '/.git/*', '*.keep', '*.gitmodules']

        self.items += self._parse_ignore_file(self.ignore)
        self.items += self._parse_ignore_file(self.exclude)

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
        self.items += self.hard_ignore

    def _parse_ignore_file(self, ignore_file):
        items = []

        if ignore_file and os.path.exists(ignore_file):
            with open(ignore_file) as gitignore:
                for item in gitignore.readlines():
                    item = item.strip()
                    if item and not item.startswith('#'):
                        items.append(item)
        return items

    def _parse_hard_ignore(self, hard_ignore):
        if isinstance(hard_ignore, basestring):
            return hard_ignore.split("|")
        else:
            return []

    def __contains__(self, path):
        return self.check_key(path)

    def check_key(self, key):
        for item in self.items:
            if self._check_item_and_key(item, key):
                return True
        return False

    def _check_item_and_key(self, item, key):
        if key.startswith("/"):
            key = key[1:]

        if item == key:
            return True

        if item.endswith("/") and key.startswith(item):
            return True

        return fnmatch.fnmatch(key, item)
