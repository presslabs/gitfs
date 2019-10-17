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


from stat import S_IFDIR, S_IFREG

import pytest
from mock import MagicMock, patch

from pygit2 import GIT_FILEMODE_TREE
from fuse import FuseOSError

from gitfs.views.commit import CommitView


class TestCommitView(object):
    def test_readdir_without_tree_name(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()

        mocked_entry.name = "entry"
        mocked_commit.tree = [mocked_entry]
        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        with patch("gitfs.views.commit.os") as mocked_os:
            mocked_os.path.split.return_value = [None, None]

            dirs = [entry for entry in view.readdir("/path", 0)]
            assert dirs == [".", "..", "entry"]

            mocked_os.path.split.assert_called_once_with("/path")

    def test_readdir_with_tree_name(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()

        mocked_entry.name = "entry"
        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_git_object.return_value = [mocked_entry]

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        with patch("gitfs.views.commit.os") as mocked_os:
            mocked_os.path.split.return_value = [None, True]

            dirs = [entry for entry in view.readdir("/path", 0)]
            assert dirs == [".", "..", "entry"]

            mocked_os.path.split.assert_called_once_with("/path")
            mocked_repo.get_git_object.assert_called_once_with("tree", "/path")

    def test_access_with_missing_relative_path(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")

        assert view.access("path", "mode") == 0

    def test_access_with_invalid_relative_path(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        view.relative_path = "/"

        assert view.access("path", "mode") == 0

    def test_access_with_invalid_path(self):
        mocked_repo = MagicMock()
        mocked_validation = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_validation.return_value = False

        with patch("gitfs.views.commit.split_path_into_components") as split:
            split.return_value = "elements"

            view = CommitView(repo=mocked_repo, commit_sha1="sha1")
            view._validate_commit_path = mocked_validation
            view.relative_path = "relative_path"

            with pytest.raises(FuseOSError):
                view.access("path", "mode")

            split.assert_called_once_with("relative_path")
            mocked_validation.assert_called_once_with("tree", "elements")

    def test_getattr_with_no_path(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        assert view.getattr(False, 1) is None

    def test_getattr_with_simple_path(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        stats = {"st_mode": S_IFDIR | 0o555, "st_nlink": 2}

        mocked_commit.tree = "tree"
        mocked_commit.commit_time = "now+1"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_git_object_default_stats.return_value = stats

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )
        result = view.getattr("/", 1)
        asserted_result = {
            "st_uid": 1,
            "st_gid": 1,
            "st_mtime": "now+1",
            "st_ctime": "now+1",
            "st_mode": S_IFDIR | 0o555,
            "st_nlink": 2,
        }
        assert result == asserted_result

    def test_getattr_with_invalid_object_type(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_commit.commit_time = "now+1"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_git_object_default_stats.return_value = None

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )

        with pytest.raises(FuseOSError):
            view.getattr("/path", 1)

        args = ("tree", "/path")
        mocked_repo.get_git_object_default_stats.assert_called_once_with(*args)

    def test_getattr_for_a_valid_file(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_commit.commit_time = "now+1"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_git_object_default_stats.return_value = {
            "st_mode": S_IFREG | 0o444,
            "st_size": 10,
        }

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )

        result = view.getattr("/path", 1)

        asserted_result = {
            "st_uid": 1,
            "st_gid": 1,
            "st_mtime": "now+1",
            "st_ctime": "now+1",
            "st_mode": S_IFREG | 0o444,
            "st_size": 10,
        }
        assert result == asserted_result
        args = ("tree", "/path")
        mocked_repo.get_git_object_default_stats.assert_called_once_with(*args)

    def test_readlink(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_blob_data.return_value = "link value"

        with patch("gitfs.views.commit.os") as mocked_os:
            mocked_os.path.split.return_value = ["name", "another_name"]

            view = CommitView(
                repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
            )
            assert view.readlink("/path") == "link value"
            mocked_os.path.split.assert_called_once_with("/path")
            mocked_repo.get_blob_data.assert_called_once_with("tree", "another_name")

    def test_read(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_blob_data.return_value = [1, 1, 1]

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )
        assert view.read("/path", 1, 1, 0) == [1]
        mocked_repo.get_blob_data.assert_called_once_with("tree", "/path")

    def test_validate_commit_path_with_no_entries(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )

        assert view._validate_commit_path([], "") is False

    def test_validate_commit_path_with_trees(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_entry.name = "simple_entry"
        mocked_entry.filemode = GIT_FILEMODE_TREE

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )
        result = view._validate_commit_path([mocked_entry], ["simple_entry"])
        assert result is True

    def test_validate_commit_path_with_more_than_one_entry(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()
        mocked_second_entry = MagicMock()

        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit

        mocked_second_entry.id = 1
        mocked_second_entry.name = "complex_entry"
        mocked_second_entry.filemode = GIT_FILEMODE_TREE
        mocked_entry.name = "simple_entry"
        mocked_entry.filemode = GIT_FILEMODE_TREE

        mocked_repo.__getitem__.return_value = [mocked_entry]

        view = CommitView(
            repo=mocked_repo, commit_sha1="sha1", mount_time="now", uid=1, gid=1
        )
        result = view._validate_commit_path(
            [mocked_second_entry, mocked_entry], ["complex_entry", "simple_entry"]
        )
        assert result is True
        mocked_repo.__getitem__.assert_called_once_with(1)

    def test_init_with_invalid_commit_sha1(self):
        mocked_repo = MagicMock()
        mocked_repo.revparse_single.side_effect = KeyError

        with pytest.raises(FuseOSError):
            CommitView(repo=mocked_repo, commit_sha1="sha1")

        mocked_repo.revparse_single.assert_called_once_with("sha1")
