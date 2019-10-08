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


import pytest
from mock import MagicMock

from gitfs.cache.base import Cache


class TestBaseCache(object):
    def test_base_setitem_insane_size_on_cache_element(self):
        cache = Cache(0, getsizeof=lambda x: 1)

        with pytest.raises(ValueError):
            cache["key"] = "item"

    def test_base_setitem_when_current_size_is_to_big(self):
        mocked_pop = MagicMock(side_effect=ValueError)

        cache = Cache(1)

        cache._Cache__currsize = 2
        cache.__maxsize = 1
        cache.popitem = mocked_pop

        with pytest.raises(ValueError):
            cache["key"] = "item"

    def test_setitem(self):
        cache = Cache(1)

        cache["key"] = 1
        cache["key"] = 2

        assert cache["key"] == 2
        assert cache.currsize == 1

    def test_delitem(self):
        cache = Cache(1)

        cache["key"] = 1
        del cache["key"]

        with pytest.raises(KeyError):
            cache["key"]

        assert cache.currsize == 0

    def test_aux_method(self):
        cache = Cache(1)

        cache["key"] = 1
        for key in cache:
            assert key == "key"
            assert cache["key"] == 1

        assert len(cache) == 1
        assert repr(cache) == "Cache([('key', 1)], maxsize=1, currsize=1)"
        assert cache.maxsize == 1
