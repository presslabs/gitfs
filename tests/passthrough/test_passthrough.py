import __builtin__
import os
from pytest import raises
from fuse import FuseOSError
from mock import MagicMock, patch, call

from gitfs.views import PassthroughView


class TestPassthrough(object):

    def setup(self):
        def mock_super(*args, **kwargs):
            if args and issubclass(PassthroughView, args[0]):
                return MagicMock()

            return original_super(*args, **kwargs)

        __builtin__.original_super = super
        __builtin__.super = mock_super

        self.repo_path = '/the/root/path'


    def teardown(self):
        __builtin__.super = __builtin__.original_super
        del __builtin__.original_super


    def test_access(self):
        mocked_access = MagicMock()
        mocked_access.side_effect = [True, True, False]

        with patch('gitfs.views.passthrough.os.access', mocked_access):
            view = PassthroughView(repo_path=self.repo_path)

            # normal, easy test
            view.access('good/relative/path', 777)
            # test if _full_path works
            view.access('/good/relative/path', 777)
            # test if proper exception is raised
            with raises(FuseOSError):
                view.access('/relative/path', 777)

            mocked_access.assert_has_calls([call('/the/root/path/good/relative/path', 777),
                                            call('/the/root/path/good/relative/path', 777),
                                            call('/the/root/path/relative/path', 777)])
            assert mocked_access.call_count == 3

    def test_chmod(self):
        mocked_chmod = MagicMock()
        with patch('gitfs.views.passthrough.os.chmod', mocked_chmod):
            view = PassthroughView(repo_path=self.repo_path)

            view.chmod('/magic/path', 777)

            mocked_chmod.assert_called_once_with('/the/root/path/magic/path', 777)

