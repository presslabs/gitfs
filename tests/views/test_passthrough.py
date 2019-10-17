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


from io import TextIOWrapper
from mock import MagicMock, patch, call
import os

from fuse import FuseOSError
from six.moves import builtins
from pytest import raises

from gitfs.views import PassthroughView


class TestPassthrough(object):
    def setup(self):
        root = "/the/root/path"

        def _full_path(partial):
            if partial.startswith("/"):
                partial = partial[1:]
            return os.path.join(root, partial)

        mocked_repo = MagicMock(_full_path=_full_path)
        self.repo = mocked_repo
        self.repo_path = root

    def test_access(self):
        mocked_access = MagicMock()
        mocked_access.side_effect = [True, True, False]

        with patch("gitfs.views.passthrough.os.access", mocked_access):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)

            # normal, easy test
            view.access("good/relative/path", 777)
            # test if _full_path works
            view.access("/good/relative/path", 777)
            # test if proper exception is raised
            with raises(FuseOSError):
                view.access("/relative/path", 777)

            asserted_calls = [
                call("/the/root/path/good/relative/path", 777),
                call("/the/root/path/good/relative/path", 777),
                call("/the/root/path/relative/path", 777),
            ]
            mocked_access.assert_has_calls(asserted_calls)
            assert mocked_access.call_count == 3

    def test_chmod(self):
        mocked_chmod = MagicMock()

        with patch("gitfs.views.passthrough.os.chmod", mocked_chmod):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)

            view.chmod("/magic/path", 0o777)

            mocked_chmod.assert_called_once_with("/the/root/path/magic/path", 0o777)

    def test_chown(self):
        mocked_chown = MagicMock()

        with patch("gitfs.views.passthrough.os.chown", mocked_chown):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)

            view.chown("/magic/path", 1000, 1000)

            mocked_chown.assert_called_once_with(
                "/the/root/path/magic/path", 1000, 1000
            )

    def test_getattr(self):
        mocked_lstat = MagicMock()
        mock_result = MagicMock()

        stats = (
            "st_atime",
            "st_ctime",
            "st_gid",
            "st_mode",
            "st_mtime",
            "st_nlink",
            "st_size",
            "st_uid",
        )
        for stat in stats:
            setattr(mock_result, stat, "mock_stat")

        mocked_lstat.return_value = mock_result

        with patch("gitfs.views.passthrough.os.lstat", mocked_lstat):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.getattr("/magic/path", 0)

            mocked_lstat.assert_called_once_with("/the/root/path/magic/path")

            assert result == dict((key, getattr(mock_result, key)) for key in stats)

    def test_stats(self):
        mocked_statvfs = MagicMock()
        mock_result = MagicMock()

        stats = (
            "f_bavail",
            "f_bfree",
            "f_blocks",
            "f_bsize",
            "f_favail",
            "f_ffree",
            "f_files",
            "f_flag",
            "f_frsize",
            "f_namemax",
        )
        for stat in stats:
            setattr(mock_result, stat, "mock_stat")

        mocked_statvfs.return_value = mock_result

        with patch("gitfs.views.passthrough.os.statvfs", mocked_statvfs):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.statfs("/magic/path")

            mocked_statvfs.assert_called_once_with("/the/root/path/magic/path")

            assert result == dict((key, getattr(mock_result, key)) for key in stats)

    def test_readdir(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join
        mocked_os.path.is_dir.return_value = True
        mocked_os.listdir.return_value = ["one_dir", "one_file", ".git"]

        with patch.multiple("gitfs.views.passthrough", os=mocked_os):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.readdir("/magic/path", 0)
            dirents = [directory for directory in result]

            assert dirents == [".", "..", "one_dir", "one_file"]
            path = "/the/root/path/magic/path"
            mocked_os.path.isdir.assert_called_once_with(path)
            mocked_os.listdir.assert_called_once_with(path)

    def test_readlink_with_slash(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join

        mocked_os.readlink.return_value = "/my_link"
        mocked_os.path.relpath.return_value = "with_slash"

        with patch("gitfs.views.passthrough.os", mocked_os):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.readlink("/magic/path")

            assert result == "with_slash"
            path = "/the/root/path/magic/path"
            mocked_os.readlink.assert_called_once_with(path)
            mocked_os.path.relpath.assert_called_once_with("/my_link", self.repo_path)

    def test_readlink_without_slash(self):
        mocked_os = MagicMock()
        mocked_os.path.join = os.path.join

        mocked_os.readlink.return_value = "my_link"

        with patch("gitfs.views.passthrough.os", mocked_os):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.readlink("/magic/path")

            assert result == "my_link"
            path = "/the/root/path/magic/path"
            mocked_os.readlink.assert_called_once_with(path)

    def test_mknod(self):
        mocked_mknod = MagicMock()
        mocked_mknod.return_value = "new_node"

        with patch("gitfs.views.passthrough.os.mknod", mocked_mknod):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.mknod("/magic/path", "mode", "dev")

            assert result == "new_node"
            path = "/the/root/path/magic/path"
            mocked_mknod.assert_called_once_with(path, "mode", "dev")

    def test_rmdir(self):
        mocked_rmdir = MagicMock()
        mocked_rmdir.return_value = "rm_dir"

        with patch("gitfs.views.passthrough.os.rmdir", mocked_rmdir):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.rmdir("/magic/path")

            assert result == "rm_dir"
            path = "/the/root/path/magic/path"
            mocked_rmdir.assert_called_once_with(path)

    def test_mkdir(self):
        mocked_mkdir = MagicMock()
        mocked_mkdir.return_value = "mk_dir"

        with patch("gitfs.views.passthrough.os.mkdir", mocked_mkdir):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.mkdir("/magic/path", "mode")

            assert result == "mk_dir"
            path = "/the/root/path/magic/path"
            mocked_mkdir.assert_called_once_with(path, "mode")

    def test_unlink(self):
        mocked_unlink = MagicMock()
        mocked_unlink.return_value = "magic"

        with patch("gitfs.views.passthrough.os.unlink", mocked_unlink):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.unlink("/magic/path")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            mocked_unlink.assert_called_once_with(path)

    def test_symlink(self):
        mocked_symlink = MagicMock()
        mocked_symlink.return_value = "magic"

        with patch("gitfs.views.passthrough.os.symlink", mocked_symlink):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.symlink("/magic/path", "/magic/link")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            link = "/the/root/path/magic/link"
            mocked_symlink.assert_called_once_with(path, link)

    def test_rename(self):
        mocked_rename = MagicMock()
        mocked_rename.return_value = "magic"

        with patch("gitfs.views.passthrough.os.rename", mocked_rename):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.rename("/magic/path", "/magic/new")

            assert result == "magic"
            old = "/the/root/path/magic/path"
            new = "/the/root/path/magic/new"
            mocked_rename.has_calls([call(old), call(new)])

    def test_link(self):
        mocked_link = MagicMock()
        mocked_link.return_value = "magic"

        with patch("gitfs.views.passthrough.os.link", mocked_link):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.link("/magic/path", "/magic/link")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            link = "/the/root/path/magic/link"
            mocked_link.assert_called_once_with(path, link)

    def test_utimes(self):
        mocked_utimes = MagicMock()
        mocked_utimes.return_value = "magic"

        with patch("gitfs.views.passthrough.os.utime", mocked_utimes):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.utimens("/magic/path", "times")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            mocked_utimes.assert_called_once_with(path, "times")

    def test_open(self):
        mocked_open = MagicMock()
        mocked_open.return_value = "magic"

        with patch("gitfs.views.passthrough.os.open", mocked_open):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.open("/magic/path", "flags")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            mocked_open.assert_called_once_with(path, "flags")

    def test_create(self):
        mocked_create = MagicMock()
        mocked_create.return_value = "magic"

        with patch("gitfs.views.passthrough.os.open", mocked_create):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.create("/magic/path", "flags")

            assert result == "magic"
            path = "/the/root/path/magic/path"
            mocked_create.assert_called_once_with(
                path, os.O_WRONLY | os.O_CREAT, "flags"
            )

    def test_read(self):
        mocked_read = MagicMock()
        mocked_lseek = MagicMock()
        mocked_read.return_value = "magic"

        with patch("gitfs.views.passthrough.os.read", mocked_read):
            with patch("gitfs.views.passthrough.os.lseek", mocked_lseek):
                view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
                result = view.read("/magic/path", 10, 10, 0)

                assert result == "magic"
                mocked_read.assert_called_once_with(0, 10)
                mocked_lseek.assert_called_once_with(0, 10, os.SEEK_SET)

    def test_write(self):
        mocked_write = MagicMock()
        mocked_lseek = MagicMock()
        mocked_write.return_value = "magic"

        with patch("gitfs.views.passthrough.os.write", mocked_write):
            with patch("gitfs.views.passthrough.os.lseek", mocked_lseek):
                view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
                result = view.write("/magic/path", 10, 10, 0)

                assert result == "magic"
                mocked_write.assert_called_once_with(0, 10)
                mocked_lseek.assert_called_once_with(0, 10, os.SEEK_SET)

    def test_flush(self):
        mocked_fsync = MagicMock()
        mocked_fsync.return_value = "magic"

        with patch("gitfs.views.passthrough.os.fsync", mocked_fsync):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.flush("/magic/path", 0)

            assert result == "magic"
            mocked_fsync.assert_called_once_with(0)

    def test_release(self):
        mocked_close = MagicMock()
        mocked_close.return_value = "magic"

        with patch("gitfs.views.passthrough.os.close", mocked_close):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.release("/magic/path", 0)

            assert result == "magic"
            mocked_close.assert_called_once_with(0)

    def test_fsync(self):
        mocked_fsync = MagicMock()
        mocked_fsync.return_value = "magic"

        with patch("gitfs.views.passthrough.os.fsync", mocked_fsync):
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            result = view.fsync("/magic/path", "data", 0)

            assert result == "magic"
            mocked_fsync.assert_called_once_with(0)

    def test_truncate(self):
        mocked_open = MagicMock()
        mocked_file = MagicMock(spec=TextIOWrapper)

        with patch("gitfs.views.passthrough.open", create=True) as mocked_open:
            mocked_open().__enter__.return_value = mocked_file
            view = PassthroughView(repo=self.repo, repo_path=self.repo_path)
            view.truncate("/magic/path", 0, 0)

            mocked_open.has_calls([call("/the/root/path/magic/path", "r+")])
            mocked_file.truncate.assert_called_once_with(0)
