import functools
import collections

try:
    from threading import RLock
except ImportError:
    from dummy_threading import RLock

from gitfs.cache import lru_cache


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


def lru_wrapper(maxsize=None, typed=False, getsizeof=None, lock=RLock):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Recently Used (LRU)
    algorithm.

    """

    if maxsize is not None:
        lru_cache.maxsize = maxsize

    makekey = _makekey_typed if typed else _makekey
    return _cachedfunc(lru_cache, makekey, lock())
