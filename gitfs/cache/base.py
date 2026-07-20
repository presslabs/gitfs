# Copyright 2014-2016 Presslabs SRL
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

import collections


class Cache(collections.abc.MutableMapping):
    """Mutable mapping to serve as a simple cache or cache base class.

    This class discards arbitrary items using :meth:`popitem` to make
    space when necessary.  Derived classes may override
    :meth:`popitem` to implement specific caching strategies.  If a
    subclass has to keep track of item access, insertion or deletion,
    it may need override :meth:`__getitem__`, :meth:`__setitem__` and
    :meth:`__delitem__`, too.

    """

    def __init__(self, maxsize, getsizeof=None):
        if getsizeof is not None:
            self.getsizeof = getsizeof

        self.__mapping = dict()
        self.__maxsize = maxsize
        self.__currsize = 0

    def __contains__(self, key):
        return key in self.__mapping

    def __getitem__(self, key):
        return self.__mapping[key][0]

    def __setitem__(self, key, value):
        mapping = self.__mapping
        maxsize = self.__maxsize
        size = self.getsizeof(value)

        if size > maxsize:
            raise ValueError("value too large")

        if key not in mapping or mapping[key][1] < size:
            while self.__currsize + size > maxsize:
                self.popitem()

        if key in mapping:
            self.__currsize -= mapping[key][1]

        mapping[key] = (value, size)
        self.__currsize += size

    def __delitem__(self, key):
        _, size = self.__mapping.pop(key)
        self.__currsize -= size

    def __iter__(self):
        return iter(self.__mapping)

    def __len__(self):
        return len(self.__mapping)

    def __repr__(self):
        return "%s(%r, maxsize=%d, currsize=%d)" % (
            self.__class__.__name__,
            list(self.items()),
            self.__maxsize,
            self.__currsize,
        )

    @property
    def maxsize(self):
        """Return the maximum size of the cache."""
        return self.__maxsize

    @maxsize.setter
    def maxsize(self, size):
        """Set maximum size of the cache."""
        self.__maxsize = size

    @property
    def currsize(self):
        """Return the current size of the cache."""
        return self.__currsize

    @staticmethod
    def getsizeof(value):
        """Return the size of a cache element."""
        return 1
