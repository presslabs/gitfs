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
