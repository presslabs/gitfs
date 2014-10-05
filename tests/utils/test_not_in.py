from fuse import FuseOSError
from mock import MagicMock, patch
import pytest
from gitfs.cache import CachedIgnore
from gitfs.utils.decorators.not_in import not_in


class TestNotIn(object):
    def test_decorator(self):
        mocked_function = MagicMock()
        mocked_function.__name__ = "function"
        mocked_object = MagicMock()
        mocked_object.ignore = CachedIgnore()
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]

        with patch.multiple("gitfs.utils.decorators.not_in",
                            inspect=mocked_inspect):
            not_in("ignore", check=["file"])(mocked_function)(mocked_object,
                                                              "file")

        mocked_function.assert_called_once_with(mocked_object, "file")

    def test_in_cache(self):
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]
        mocked_gitignore = MagicMock()
        mocked_gitignore.get.return_value = True
        mocked_look_at = MagicMock()
        mocked_look_at.cache = mocked_gitignore

        with patch.multiple("gitfs.utils.decorators.not_in",
                            inspect=mocked_inspect):
            with pytest.raises(FuseOSError):
                not_in(mocked_look_at, check=["file"]).check_args(None, "file")

    def test_has_key(self):
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]
        mocked_gitignore = MagicMock()
        mocked_gitignore.get.return_value = False
        mocked_look_at = MagicMock()
        mocked_look_at.cache = mocked_gitignore
        mocked_look_at.check_key.return_value = True

        with patch.multiple("gitfs.utils.decorators.not_in",
                            inspect=mocked_inspect):
            with pytest.raises(FuseOSError):
                not_in(mocked_look_at, check=["file"]).check_args(None, "file")
