from mock import MagicMock, patch

from gitfs.cache.lru import LRUCache


class TestLRUCache(object):
    def test_getitem(self):
        mocked_getitem = MagicMock()
        mocked_link = MagicMock()
        mocked_root = MagicMock()
        mocked_node = MagicMock(return_value=mocked_root)

        mocked_getitem.return_value = ("value1", mocked_link)

        from gitfs.cache.lru import Cache
        old_getitem = Cache.__getitem__
        Cache.__getitem__ = mocked_getitem

        with patch.multiple('gitfs.cache.lru', Node=mocked_node):
            lru = LRUCache(1)
            lru["key"] = "value"

            assert lru["key"] == "value1"
            mocked_getitem.asset_called_once_with("key")
            assert mocked_link.next.prev == mocked_link.prev
            assert mocked_link.prev.next == mocked_link.next
            assert mocked_link.prev == mocked_root.prev
            assert mocked_link.next == mocked_root
            assert mocked_root.next == mocked_link
            assert mocked_root.prev == mocked_link

        Cache.__getitem__ = old_getitem
