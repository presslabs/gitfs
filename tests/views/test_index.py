import pytest

from fuse import FuseOSError

from gitfs.views.index import IndexView


class TestIndexView(object):
    def test_getattr_with_non_root_path(self):
        view = IndexView()

        with pytest.raises(FuseOSError):
            view.getattr("/path")
