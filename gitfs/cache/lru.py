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


try:
    from threading import RLock
except ImportError:
    from dummy_threading import RLock


from .base import Cache
from .node import Node


class LRUCache(Cache):
    """Least Recently Used (LRU) cache implementation.

    This class discards the least recently used items first to make
    space when necessary.

    """

    def __init__(self, maxsize, getsizeof=None):
        if getsizeof is not None:
            Cache.__init__(self, maxsize, lambda e: getsizeof(e[0]))
        else:
            Cache.__init__(self, maxsize)

        root = Node()
        root.prev = root.next = root
        self.__root = root

        self.__lock = RLock()

    def __getitem__(self, key):
        value, link = super(LRUCache, self).__getitem__(key)
        root = self.__root
        link.prev.next = link.next
        link.next.prev = link.prev
        link.prev = tail = root.prev
        link.next = root
        tail.next = root.prev = link
        return value

    def __setitem__(self, key, value):
        with self.__lock:
            try:
                _, link = super(LRUCache, self).__getitem__(key)
            except KeyError:
                link = Node()

            super(LRUCache, self).__setitem__(key, (value, link))

            try:
                link.prev.next = link.next
                link.next.prev = link.prev
            except AttributeError:
                link.data = key

            root = self.__root
            link.prev = tail = root.prev
            link.next = root
            tail.next = root.prev = link

    def __delitem__(self, key):
        with self.__lock:
            _, link = super(LRUCache, self).__getitem__(key)
            super(LRUCache, self).__delitem__(key)

            link.prev.next = link.next
            link.next.prev = link.prev

            del link.next
            del link.prev

    def __repr__(self):
        return '%s(%r, maxsize=%d, currsize=%d)' % (
            self.__class__.__name__,
            [(key, super(LRUCache, self).__getitem__(key)[0]) for key in self],
            self.maxsize,
            self.currsize,
        )

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""

        with self.__lock:
            root = self.__root
            link = root.next

            if link is root:
                raise KeyError('cache is empty')

            key = link.data
            return (key, self.pop(key))

    def get_if_exists(self, key):
        with self.__lock:
            exists = super(LRUCache, self).__contains__(key)
            if not exists:
                return None

            return self.__getitem__(key)
