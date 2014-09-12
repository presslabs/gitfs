from stat import S_IFDIR

import pytest

from fuse import FuseOSError

from gitfs.views.index import IndexView


class TestIndexView(object):
    def test_getattr_with_non_root_path(self):
        view = IndexView()

        with pytest.raises(FuseOSError):
            view.getattr("/path")

    def test_getattr_with_correct_path(self):
        view = IndexView(**{
            'uid': 1,
            'gid': 1,
            'mount_time': "now"
        })
        result = view.getattr("/", 1)

        asserted_result = {
            'st_mode': S_IFDIR | 0555,
            'st_nlink': 2,
            'st_uid': 1,
            'st_gid': 1,
            'st_ctime': "now",
            'st_mtime': "now",
        }
        assert result == asserted_result

    def test_readdir(self):
        view = IndexView()
        assert view.readdir("path", 1) == ['.', '..', 'current', 'history']
