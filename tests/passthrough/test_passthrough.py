import __builtin__
import os
from pytest import raises
from fuse import FuseOSError
from mock import MagicMock, patch, call

from gitfs.views import PassthroughView


"""
TODO:
    def getattr(self, path, fh=None):
    def readdir(self, path, fh):
    def readlink(self, path):
    def mknod(self, path, mode, dev):
    def rmdir(self, path):
    def mkdir(self, path, mode):
    def statfs(self, path):
    def unlink(self, path):
    def symlink(self, target, name):
    def rename(self, old, new):
    def link(self, target, name):
    def utimens(self, path, times=None):
    def open(self, path, flags):
    def create(self, path, mode, fi=None):
    def read(self, path, length, offset, fh):
    def write(self, path, buf, offset, fh):
    def truncate(self, path, length, fh=None):
    def flush(self, path, fh):
    def release(self, path, fh):
    def fsync(self, path, fdatasync, fh):
"""


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

            asserted_calls = [call('/the/root/path/good/relative/path', 777),
                              call('/the/root/path/good/relative/path', 777),
                              call('/the/root/path/relative/path', 777)]
            mocked_access.assert_has_calls(asserted_calls)
            assert mocked_access.call_count == 3

    def test_chmod(self):
        mocked_chmod = MagicMock()

        with patch('gitfs.views.passthrough.os.chmod', mocked_chmod):
            view = PassthroughView(repo_path=self.repo_path)

            view.chmod('/magic/path', 777)

            mocked_chmod.assert_called_once_with('/the/root/path/magic/path',
                                                 777)

    def test_chown(self):
        mocked_chown = MagicMock()

        with patch('gitfs.views.passthrough.os.chown', mocked_chown):
            view = PassthroughView(repo_path=self.repo_path)

            view.chown('/magic/path', 1000, 1000)

            mocked_chown.assert_called_once_with('/the/root/path/magic/path',
                                                 1000, 1000)

    def test_getattr(self):
        mocked_lstat = MagicMock()
        mock_result = MagicMock()

        STATS = ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid')
        for stat in STATS:
            setattr(mock_result, stat, "mock_stat")

        mocked_lstat.return_value = mock_result

        with patch('gitfs.views.passthrough.os.lstat', mocked_lstat):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.getattr('/magic/path', 0)

            mocked_lstat.assert_called_once_with("/the/root/path/magic/path")

            assert result == dict((key, getattr(mock_result, key))
                                  for key in STATS)
