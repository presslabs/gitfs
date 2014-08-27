import __builtin__
import os
from pytest import raises
from fuse import FuseOSError
from mock import MagicMock, patch, call

from gitfs.views import PassthroughView


"""
TODO:
    def statfs(self, path):
    def truncate(self, path, length, fh=None):
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

        stats = ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime',
                 'st_nlink', 'st_size', 'st_uid')
        for stat in stats:
            setattr(mock_result, stat, "mock_stat")

        mocked_lstat.return_value = mock_result

        with patch('gitfs.views.passthrough.os.lstat', mocked_lstat):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.getattr('/magic/path', 0)

            mocked_lstat.assert_called_once_with("/the/root/path/magic/path")

            assert result == dict((key, getattr(mock_result, key))
                                  for key in stats)

    def test_readdir(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join
        mocked_os.path.is_dir.return_value = True
        mocked_os.listdir.return_value = ['one_dir', 'one_file', '.git']

        with patch.multiple('gitfs.views.passthrough', os=mocked_os):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.readdir("/magic/path", 0)
            dirents = [directory for directory in result]

            assert dirents == ['.', '..', 'one_dir', 'one_file']
            path = '/the/root/path/magic/path'
            mocked_os.path.isdir.assert_called_once_with(path)
            mocked_os.listdir.assert_called_once_with(path)

    def test_readlink_with_slash(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join

        mocked_os.readlink.return_value = "/my_link"
        mocked_os.path.relpath.return_value = "with_slash"

        with patch('gitfs.views.passthrough.os', mocked_os):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.readlink("/magic/path")

            assert result == "with_slash"
            path = '/the/root/path/magic/path'
            mocked_os.readlink.assert_called_once_with(path)
            mocked_os.path.relpath.assert_called_once_with("/my_link",
                                                           self.repo_path)

    def test_readlink_without_slash(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join

        mocked_os.readlink.return_value = "my_link"

        with patch('gitfs.views.passthrough.os', mocked_os):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.readlink("/magic/path")

            assert result == "my_link"
            path = '/the/root/path/magic/path'
            mocked_os.readlink.assert_called_once_with(path)

    def test_mknod(self):
        mocked_mknod = MagicMock()
        mocked_mknod.return_value = "new_node"

        with patch('gitfs.views.passthrough.os.mknod', mocked_mknod):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.mknod("/magic/path", "mode", "dev")

            assert result == "new_node"
            path = '/the/root/path/magic/path'
            mocked_mknod.assert_called_once_with(path, "mode", "dev")

    def test_rmdir(self):
        mocked_rmdir = MagicMock()
        mocked_rmdir.return_value = "rm_dir"

        with patch('gitfs.views.passthrough.os.rmdir', mocked_rmdir):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.rmdir("/magic/path")

            assert result == "rm_dir"
            path = '/the/root/path/magic/path'
            mocked_rmdir.assert_called_once_with(path)

    def test_mkdir(self):
        mocked_mkdir = MagicMock()
        mocked_mkdir.return_value = "mk_dir"

        with patch('gitfs.views.passthrough.os.mkdir', mocked_mkdir):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.mkdir("/magic/path", "mode")

            assert result == "mk_dir"
            path = '/the/root/path/magic/path'
            mocked_mkdir.assert_called_once_with(path, "mode")

    def test_unlink(self):
        mocked_unlink = MagicMock()
        mocked_unlink.return_value = "magic"

        with patch('gitfs.views.passthrough.os.unlink', mocked_unlink):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.unlink("/magic/path")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            mocked_unlink.assert_called_once_with(path)

    def test_symlink(self):
        mocked_symlink = MagicMock()
        mocked_symlink.return_value = "magic"

        with patch('gitfs.views.passthrough.os.symlink', mocked_symlink):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.symlink("/magic/path", "/magic/link")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            link = '/the/root/path/magic/link'
            mocked_symlink.assert_called_once_with(path, link)

    def test_rename(self):
        mocked_rename = MagicMock()
        mocked_rename.return_value = "magic"

        with patch('gitfs.views.passthrough.os.rename', mocked_rename):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.rename("/magic/path", "/magic/new")

            assert result == "magic"
            old = '/the/root/path/magic/path'
            new = '/the/root/path/magic/new'
            mocked_rename.has_calls([call(old), call(new)])

    def test_link(self):
        mocked_link = MagicMock()
        mocked_link.return_value = "magic"

        with patch('gitfs.views.passthrough.os.link', mocked_link):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.link("/magic/path", "/magic/link")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            link = '/the/root/path/magic/link'
            mocked_link.assert_called_once_with(path, link)

    def test_utimes(self):
        mocked_utimes = MagicMock()
        mocked_utimes.return_value = "magic"

        with patch('gitfs.views.passthrough.os.utime', mocked_utimes):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.utimens("/magic/path", "times")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            mocked_utimes.assert_called_once_with(path, "times")

    def test_open(self):
        mocked_open = MagicMock()
        mocked_open.return_value = "magic"

        with patch('gitfs.views.passthrough.os.open', mocked_open):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.open("/magic/path", "flags")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            mocked_open.assert_called_once_with(path, "flags")

    def test_create(self):
        mocked_create = MagicMock()
        mocked_create.return_value = "magic"

        with patch('gitfs.views.passthrough.os.open', mocked_create):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.create("/magic/path", "flags")

            assert result == "magic"
            path = '/the/root/path/magic/path'
            mocked_create.assert_called_once_with(path,
                                                  os.O_WRONLY | os.O_CREAT,
                                                  "flags")

    def test_read(self):
        mocked_read = MagicMock()
        mocked_lseek = MagicMock()
        mocked_read.return_value = "magic"

        with patch('gitfs.views.passthrough.os.read', mocked_read):
            with patch('gitfs.views.passthrough.os.lseek', mocked_lseek):
                view = PassthroughView(repo_path=self.repo_path)
                result = view.read("/magic/path", 10, 10, 0)

                assert result == "magic"
                mocked_read.assert_called_once_with(0, 10)
                mocked_lseek.assert_called_once_with(0, 10, os.SEEK_SET)

    def test_write(self):
        mocked_write = MagicMock()
        mocked_lseek = MagicMock()
        mocked_write.return_value = "magic"

        with patch('gitfs.views.passthrough.os.write', mocked_write):
            with patch('gitfs.views.passthrough.os.lseek', mocked_lseek):
                view = PassthroughView(repo_path=self.repo_path)
                result = view.write("/magic/path", 10, 10, 0)

                assert result == "magic"
                mocked_write.assert_called_once_with(0, 10)
                mocked_lseek.assert_called_once_with(0, 10, os.SEEK_SET)

    def test_flush(self):
        mocked_fsync = MagicMock()
        mocked_fsync.return_value = "magic"

        with patch('gitfs.views.passthrough.os.fsync', mocked_fsync):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.flush("/magic/path", 0)

            assert result == "magic"
            mocked_fsync.assert_called_once_with(0)

    def test_release(self):
        mocked_close = MagicMock()
        mocked_close.return_value = "magic"

        with patch('gitfs.views.passthrough.os.close', mocked_close):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.release("/magic/path", 0)

            assert result == "magic"
            mocked_close.assert_called_once_with(0)

    def test_fsync(self):
        mocked_fsync = MagicMock()
        mocked_fsync.return_value = "magic"

        with patch('gitfs.views.passthrough.os.fsync', mocked_fsync):
            view = PassthroughView(repo_path=self.repo_path)
            result = view.fsync("/magic/path", "data", 0)

            assert result == "magic"
            mocked_fsync.assert_called_once_with(0)
