import pytest

from fuse import FuseOSError

from gitfs.views.read_only import ReadOnlyView


class TestReadOnly(object):
    def test_cant_write(self):
        view = ReadOnlyView()

        for method in ["getxattr", "write", "create", "utimens",
                       "chmod", "mkdir"]:
            with pytest.raises(FuseOSError):
                getattr(view, method)("path", 1)

        with pytest.raises(FuseOSError):
            view.chown("path", 1, 1)
