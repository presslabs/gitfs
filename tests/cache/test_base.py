import pytest
from mock import MagicMock

from gitfs.cache.base import Cache


class TestBaseCache(object):
    def test_base_setitem_insane_size_on_cache_element(self):
        cache = Cache(0, getsizeof=lambda x: 1)

        with pytest.raises(ValueError):
            cache['key'] = "item"

    def test_base_setitem_when_current_size_is_to_big(self):
        mocked_pop = MagicMock(side_effect=ValueError)

        cache = Cache(1)

        cache._Cache__currsize = 2
        cache.__maxsize = 1
        cache.popitem = mocked_pop

        with pytest.raises(ValueError):
            cache['key'] = "item"

    def test_setitem(self):
        cache = Cache(1)

        cache['key'] = 1
        cache['key'] = 2

        assert cache['key'] == 2
        assert cache._Cache__currsize == 1
