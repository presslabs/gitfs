from threading import Event

import pytest
from mock import patch, MagicMock

from fuse import FuseOSError
from gitfs.views.current import CurrentView


class TestCurrentView(object):
    def test_rename(self):
        mocked_re = MagicMock()
        mocked_index = MagicMock()
        mocked_os = MagicMock()
        mocked_result = MagicMock()

        mocked_result.rename.return_value = True
        mocked_re.sub.return_value = "new"
        mocked_os.path.split.return_value = [1, 1]

        with patch.multiple('gitfs.views.current', re=mocked_re,
                            os=mocked_os):
            from gitfs.views import current
            current.PassthroughView.rename = lambda self, old, new: True

            current = CurrentView(regex="regex", repo_path="repo_path",
                                  read_only=Event(), want_to_merge=Event())
            current._index = mocked_index

            result = current.rename("old", "new")
            assert result is True
            mocked_index.assert_called_once_with(**{
                'remove': 1,
                'add': "new",
                "message": "Rename old to new"
            })
            mocked_os.path.split.assert_called_once_with("old")

    def test_rename_in_git_dir(self):
        current = CurrentView(repo_path="repo",
                              read_only=Event(), want_to_merge=Event())
        with pytest.raises(FuseOSError):
            current.rename(".git/", ".git/")

    def test_symlink(self):
        mocked_index = MagicMock()
        mocked_full_path = MagicMock()

        mocked_full_path.return_value = "full_path"

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.symlink.return_value = "done"

            current = CurrentView(repo_path="repo",
                                  read_only=Event(), want_to_merge=Event())
            current._index = mocked_index
            current._full_path = mocked_full_path

            assert current.symlink("name", "target") == "done"
            mocked_os.symlink.assert_called_once_with("target", "full_path")
            mocked_full_path.assert_called_once_with("name")
            message = "Create symlink to target for name"
            mocked_index.assert_called_once_with(add="name", message=message)

    def test_readlink(self):
        mocked_full_path = MagicMock()
        mocked_full_path.return_value = "full path"

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.readlink.return_value = "done"

            current = CurrentView(repo_path="repo",
                                  read_only=Event(), want_to_merge=Event())
            current._full_path = mocked_full_path

            assert current.readlink("path") == "done"

    def test_readlink_in_git_repo(self):
        with pytest.raises(FuseOSError):
            current = CurrentView(repo_path="repo",
                                  read_only=Event(), want_to_merge=Event())
            current.readlink(".git/")

    def test_getattr(self):
        mocked_full = MagicMock()
        mocked_os = MagicMock()
        mocked_stat = MagicMock()

        mocked_stat.simple = "stat"
        mocked_os.lstat.return_value = mocked_stat
        mocked_full.return_value = "full_path"

        with patch.multiple('gitfs.views.current', os=mocked_os,
                            STATS=['simple']):
            current = CurrentView(repo_path="repo", uid=1, gid=1)
            current._full_path = mocked_full

            result = current.getattr("path")
            asserted_result = {
                'st_uid': 1,
                'st_gid': 1,
                'simple': "stat"
            }
            assert result == asserted_result

            mocked_os.lstat.assert_called_once_with("full_path")
            mocked_full.assert_called_once_with("path")

    def test_getattr_in_git_dir(self):
        with pytest.raises(FuseOSError):
            current = CurrentView(repo_path="repo", uid=1, gid=1)
            current.getattr(".git/index")

    def test_write_in_git_dir(self):
        with pytest.raises(FuseOSError):
            current = CurrentView(repo_path="repo", uid=1, gid=1,
                                  read_only=Event())
            current.write(".git/index", "buf", "offset", 1)

    def test_write_to_large_file(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event())
        current.max_size = 10
        current.dirty = {
            '/path': {
                'size': 5
            }
        }

        with pytest.raises(FuseOSError):
            current.write("/path", "bufffffert", 11, 1)

        assert current.dirty == {
            '/path': {
                'size': 5,
                'is_dirty': False,
                'delete_it': True
            }
        }

    def test_write(self):
        from gitfs.views import current
        mocked_write = lambda self, path, buf, offste, fh: "done"
        current.PassthroughView.write = mocked_write

        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event())
        current.max_offset = 20
        current.max_size = 20
        current.dirty = {
            '/path': {
                'size': 5
            }
        }

        assert current.write("/path", "bufffffert", 11, 1) == "done"
        assert current.dirty == {
            '/path': {
                'message': 'Update /path',
                'is_dirty': True,
                'size': 15
            }
        }

    def test_mkdir(self):
        from gitfs.views import current
        mocked_mkdir = lambda self, path, mode: "done"
        current.PassthroughView.mkdir = mocked_mkdir

        mocked_create = MagicMock()
        mocked_create.return_value = 1
        mocked_release = MagicMock()

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.path.exists.return_value = False
            mocked_os.path.split.return_value = [1, 1]

            current = CurrentView(repo_path="repo", uid=1, gid=1,
                                  read_only=Event(), want_to_merge=Event())
            current.create = mocked_create
            current.release = mocked_release

            assert current.mkdir("/path", "mode") == "done"
            mocked_os.path.split.assert_called_once_with("/path")
            mocked_os.path.exists.assert_called_once_with("1/.keep")
            mocked_create.assert_called_once_with("1/.keep", 0644)
            mocked_release.assert_called_once_with("1/.keep", 1)

    def test_mkdir_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), want_to_merge=Event())
        with pytest.raises(FuseOSError):
            current.mkdir(".git/", "mode")

    def test_create_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), want_to_merge=Event())
        with pytest.raises(FuseOSError):
            current.create(".git/", "mode")

    def test_create(self):
        from gitfs.views import current
        current.PassthroughView.create = lambda self, path, mode, fi: "done"

        mocked_writing = MagicMock()
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), want_to_merge=Event(),
                              somebody_is_writing=mocked_writing)
        current.dirty = {
            '/path': {
                'content': "here"
            }
        }

        assert current.create("/path", "mode") == "done"
        assert mocked_writing.set.call_count == 1
        assert mocked_writing.clear.call_count == 1
        assert current.dirty == {
            '/path': {
                'message': "Created /path",
                'is_dirty': True,
                'size': 0
            }
        }

    def test_chmod_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), want_to_merge=Event())
        with pytest.raises(FuseOSError):
            current.chmod(".git/", "mode")
