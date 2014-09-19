import pytest

from gitfs.cache.lru import LRUCache, lru_cache


@lru_cache(maxsize=2)
def cached(n):
    return n


class TestLRUCache(object):
    def test_insert(self):
        lru = LRUCache(2)

        lru[1] = 1
        lru[2] = 2
        lru[3] = 3

        assert len(lru) == 2
        assert lru[2] == 2
        assert lru[3] == 3
        assert 1 not in lru

        lru[2]
        lru[4] = 4
        assert len(lru) == 2
        assert lru[2] == 2
        assert lru[4] == 4
        assert 3 not in lru

        lru[5] = 5
        assert len(lru) == 2
        assert lru[4] == 4
        assert lru[5] == 5
        assert 2 not in lru

    def test_lru_getsizeof(self):
        lru = LRUCache(3, lambda x: x)

        lru[1] = 1
        lru[2] = 2

        assert len(lru) == 2
        assert lru[1] == 1
        assert lru[2] == 2

        lru[3] = 3

        assert len(lru) == 1
        assert lru[3] == 3
        assert 1 not in lru
        assert 2 not in lru

        with pytest.raises(ValueError):
            lru[4] = 4

        assert len(lru) == 1
        assert lru[3] == 3

    def test_decorator(self):
        assert cached.cache_info() == (0, 0, 2, 0)
        assert cached(1) == 1
        assert cached.cache_info() == (0, 1, 2, 1)
        assert cached(1) == 1
        assert cached.cache_info() == (1, 1, 2, 1)
        assert cached(1.0) == 1.0
        assert cached.cache_info() == (2, 1, 2, 1)

        cached.cache_clear()

        assert cached(1) == 1
        assert cached.cache_info() == (2, 2, 2, 1)
