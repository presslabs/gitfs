import pytest

from gitfs.cache.base import Cache


class TestBaseCache(object):
    def test_base_setitem_insane_size_on_cache_element(self):
        cache = Cache(0, getsizeof=lambda x: 1)
        with pytest.raises(ValueError):
            cache['key'] = "item"
