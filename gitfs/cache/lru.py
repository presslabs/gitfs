import functools
import collections 
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

    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        value, link = cache_getitem(self, key)
        root = self.__root
        link.prev.next = link.next
        link.next.prev = link.prev
        link.prev = tail = root.prev
        link.next = root
        tail.next = root.prev = link
        return value

    def __setitem__(self, key, value,
                    cache_getitem=Cache.__getitem__,
                    cache_setitem=Cache.__setitem__):
        try:
            _, link = cache_getitem(self, key)
        except KeyError:
            link = Node()
        cache_setitem(self, key, (value, link))
        try:
            link.prev.next = link.next
            link.next.prev = link.prev
        except AttributeError:
            link.data = key
        root = self.__root
        link.prev = tail = root.prev
        link.next = root
        tail.next = root.prev = link

    def __delitem__(self, key,
                    cache_getitem=Cache.__getitem__,
                    cache_delitem=Cache.__delitem__):
        _, link = cache_getitem(self, key)
        cache_delitem(self, key)
        link.prev.next = link.next
        link.next.prev = link.prev
        del link.next
        del link.prev

    def __repr__(self, cache_getitem=Cache.__getitem__):
        return '%s(%r, maxsize=%d, currsize=%d)' % (
            self.__class__.__name__,
            [(key, cache_getitem(self, key)[0]) for key in self],
            self.maxsize,
            self.currsize,
        )

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""
        root = self.__root
        link = root.next
        if link is root:
            raise KeyError('cache is empty')
        key = link.data
        return (key, self.pop(key))

CacheInfo = collections.namedtuple('CacheInfo', 'hits misses maxsize currsize')


def _makekey_typed(args, kwargs):
    key = _makekey(args, kwargs)
    key += tuple(type(v) for v in args)
    key += tuple(type(v) for k, v in sorted(kwargs.items()))
    return key


def _cachedfunc(cache, makekey, lock):
    def decorator(func):
        stats = [0, 0]

        def wrapper(*args, **kwargs):
            key = makekey(args, kwargs)
            with lock:
                try:
                    result = cache[key]
                    stats[0] += 1
                    return result
                except KeyError:
                    stats[1] += 1
            result = func(*args, **kwargs)
            with lock:
                cache[key] = result
            return result

        def cache_info():
            with lock:
                hits, misses = stats
                maxsize = cache.maxsize
                currsize = cache.currsize
            return CacheInfo(hits, misses, maxsize, currsize)

        def cache_clear():
            with lock:
                cache.clear()

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return functools.update_wrapper(wrapper, func)

    return decorator


def _makekey(args, kwargs):
    return (args, tuple(sorted(kwargs.items())))


def lru_cache(maxsize=128, typed=False, getsizeof=None, lock=RLock):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Recently Used (LRU)
    algorithm.

    """
    makekey = _makekey_typed if typed else _makekey
    return _cachedfunc(LRUCache(maxsize, getsizeof), makekey, lock())
