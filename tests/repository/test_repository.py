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


import time
from collections import namedtuple
from stat import S_IFDIR, S_IFREG

import pytest
from mock import MagicMock, patch, call, ANY
from pygit2 import (
    GIT_BRANCH_REMOTE,
    GIT_SORT_TIME,
    GIT_FILEMODE_BLOB,
    GIT_STATUS_CURRENT,
)

from gitfs.repository import Repository
from .base import RepositoryBaseTest

Commit = namedtuple("Commit", "hex")


class TestRepository(RepositoryBaseTest):
    def test_push(self):
        mocked_repo = MagicMock()
        mocked_remote = MagicMock()
        mocked_remote.name = "origin"
        mocked_repo.remotes = [mocked_remote]

        repo = Repository(mocked_repo)
        repo.push("origin", "master", "credentials")

        mocked_remote.push.assert_called_once_with(
            ["refs/heads/master"], callbacks="credentials"
        )

    def test_fetch(self):
        class MockedCommit(object):
            @property
            def hex(self):
                time.sleep(0.1)
                return time.time()

        mocked_repo = MagicMock()
        mocked_remote = MagicMock()
        mocked_remote.name = "origin"

        mocked_repo.remotes = [mocked_remote]
        mocked_repo.lookup_branch().get_object.return_value = MockedCommit()
        mocked_repo.walk.return_value = [MockedCommit()]

        repo = Repository(mocked_repo)
        repo.fetch("origin", "master", "credentials")

        assert mocked_remote.fetch.call_count == 1

    def test_comit_no_parents(self):
        mocked_repo = MagicMock()
        mocked_parent = MagicMock()

        mocked_parent.id = 1

        mocked_repo.status.return_value = True
        mocked_repo.index.write_tree.return_value = "tree"
        mocked_repo.revparse_single.return_value = mocked_parent
        mocked_repo.create_commit.return_value = "commit"

        author = ("author_1", "author_2")
        commiter = ("commiter_1", "commiter_2")

        with patch("gitfs.repository.Signature") as mocked_signature:
            mocked_signature.return_value = "signature"

            repo = Repository(mocked_repo)
            commit = repo.commit("message", author, commiter)

            assert commit == "commit"
            assert mocked_repo.status.call_count == 1
            assert mocked_repo.index.write_tree.call_count == 1
            assert mocked_repo.index.write.call_count == 1

            mocked_signature.has_calls([call(*author), call(*commiter)])
            mocked_repo.revparse_single.assert_called_once_with("HEAD")
            mocked_repo.create_commit.assert_called_once_with(
                "HEAD", "signature", "signature", "message", "tree", [1]
            )

    def test_commit_with_nothing_to_commit(self):
        mocked_repo = MagicMock()
        mocked_repo.status.return_value = {}

        author = ("author_1", "author_2")
        commiter = ("commiter_1", "commiter_2")

        repo = Repository(mocked_repo)
        commit = repo.commit("message", author, commiter)

        assert commit is None

    def test_clone(self):
        mocked_repo = MagicMock()

        remote_url = "git@github.com:test/test.git"
        path = "/path/to/repo"

        with patch("gitfs.repository.clone_repository") as mocked_clone:
            mocked_clone.return_value = mocked_repo

            Repository.clone(remote_url, path)

            mocked_clone.assert_called_once_with(
                remote_url, path, checkout_branch=None, callbacks=None
            )
            assert mocked_repo.checkout_head.call_count == 1

    def test_remote_head(self):
        upstream = "origin"
        branch = "master"

        mocked_repo = MagicMock()
        mocked_remote = MagicMock()

        mocked_remote.get_object.return_value = "simple_remote"
        mocked_repo.lookup_branch.return_value = mocked_remote

        repo = Repository(mocked_repo)

        assert repo.remote_head(upstream, branch) == "simple_remote"
        assert mocked_remote.get_object.call_count == 1

        ref = "{}/{}".format(upstream, branch)
        mocked_repo.lookup_branch.assert_called_once_with(ref, GIT_BRANCH_REMOTE)

    def test_get_remote(self):
        upstream = "origin"

        mocked_repo = MagicMock()
        mocked_remote = MagicMock()

        mocked_remote.name = upstream
        mocked_repo.remotes = [mocked_remote]

        repo = Repository(mocked_repo)
        assert repo.get_remote(upstream) == mocked_remote

    def test_get_remote_with_missing_remote(self):
        mocked_repo = MagicMock()
        mocked_remote = MagicMock()

        mocked_remote.name = "fork"
        mocked_repo.remotes = [mocked_remote]

        repo = Repository(mocked_repo)
        with pytest.raises(ValueError):
            repo.get_remote("origin")

    def test_walk_branches(self):
        """
        Given 2 branches, this method whould return the commits step by step:
            [(commit_1_branch_1, commit_1_branch_2),
             (commit_2_branch_1, commit_2_branch_2),
             (commit_3_branch_1, commit_3_branch_2),
                            .
                            .
                            .
             (commit_n_branch_1, commit_n_branch_2)]
        """

        class BranchWalker(object):
            commit_number = 1

            def __init__(self, step=1, max_commit_number=10):
                self.step = step
                self.max_commit_number = max_commit_number

            def __next__(self):
                number = self.commit_number
                if self.commit_number >= self.max_commit_number:
                    raise StopIteration()
                self.commit_number += self.step
                return number

            def __iter__(self):
                yield self.commit_number
                self.commit_number += self.step
                if self.commit_number >= self.max_commit_number:
                    raise StopIteration()

        mocked_repo = MagicMock()

        def mocked_walk(target, sort):
            return BranchWalker() if target == "first" else BranchWalker(2)

        mocked_repo.walk = mocked_walk

        repo = Repository(mocked_repo)

        counter_1 = 1
        counter_2 = 1
        branches = (MagicMock(target="first"), MagicMock(target="second"))
        for commit_1, commit_2 in repo.walk_branches(GIT_SORT_TIME, *branches):
            assert commit_1 == counter_1
            assert commit_2 == counter_2

            if counter_2 < 9:
                counter_2 += 2
            counter_1 += 1

    def test_get_commits_by_dates(self):
        mocked_repo = MagicMock()
        commits = {"now": [1, 2, 3]}

        repo = Repository(mocked_repo, commits)
        assert repo.get_commits_by_date("now") == ["1", "2", "3"]

    def test_get_commit_dates(self):
        mocked_repo = MagicMock()
        commits = {"now": [1, 2, 3]}

        repo = Repository(mocked_repo, commits)
        assert repo.get_commit_dates() == ["now"]

    def test_is_searched_entry(self):
        mocked_repo = MagicMock()
        repo = Repository(mocked_repo)

        result = repo._is_searched_entry("entry", "entry", ["entry"])
        assert result

    def test_get_git_object_type(self):
        mocked_entry = MagicMock()
        mocked_entry.name = "entry"
        mocked_entry.filemode = "git_file"

        mocked_repo = MagicMock()
        repo = Repository(mocked_repo)

        mock_path = "gitfs.repository.split_path_into_components"
        with patch(mock_path) as mocked_split_path:
            mocked_split_path.return_value = ["entry"]

            result = repo.get_git_object_type([mocked_entry], "path")

            assert result == "git_file"
            mocked_split_path.assert_called_once_with("path")

    def test_get_git_object(self):
        mocked_entry = MagicMock()
        mocked_entry.name = "entry"
        mocked_entry.filemode = "git_file"

        mocked_repo = MagicMock()
        mocked_repo.__getitem__.return_value = "succed"
        repo = Repository(mocked_repo)

        mock_path = "gitfs.repository.split_path_into_components"
        with patch(mock_path) as mocked_split_path:
            mocked_split_path.return_value = ["entry"]

            result = repo.get_git_object([mocked_entry], "path")

            assert result == "succed"
            mocked_split_path.assert_called_once_with("path")

    def test_get_blob_size(self):
        mocked_repo = MagicMock()
        mocked_git_object = MagicMock()
        mocked_git_object().size = 42

        repo = Repository(mocked_repo)
        repo.get_git_object = mocked_git_object

        assert repo.get_blob_size("tree", "path") == 42
        mocked_git_object.has_calls([call("tree", "path")])

    def test_get_blob_data(self):
        mocked_repo = MagicMock()
        mocked_git_object = MagicMock()
        mocked_git_object().data = "some data"

        repo = Repository(mocked_repo)
        repo.get_git_object = mocked_git_object

        assert repo.get_blob_data("tree", "path") == "some data"
        mocked_git_object.has_calls([call("tree", "path")])

    def test_find_diverge_commits_first_from_second(self):
        mocked_repo = MagicMock()

        def walker(obj, sort, *branches):
            first_branch = [Commit(1), Commit(2), Commit(3), Commit(4)]
            second_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        repo = Repository(mocked_repo)
        repo.walk_branches = walker

        result = repo.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_find_diverge_commits_second_from_first(self):
        mocked_repo = MagicMock()

        def walker(obj, sort, *branches):
            first_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]
            second_branch = [Commit(1), Commit(2), Commit(3), Commit(4)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        repo = Repository(mocked_repo)
        repo.walk_branches = walker

        result = repo.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_find_diverge_commits_common_commit(self):
        mocked_repo = MagicMock()

        def walker(obj, sort, *branches):
            first_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]
            second_branch = [Commit(1), Commit(0), Commit(2), Commit(3)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        repo = Repository(mocked_repo)
        repo.walk_branches = walker

        result = repo.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_proxy_methods(self):
        mocked_repo = MagicMock()

        repo = Repository(mocked_repo)

        assert repo.one_attr == mocked_repo.one_attr
        assert repo["one_attr"] == mocked_repo["one_attr"]
        assert repo.behind is False

    def test_ahead(self):
        mocked_repo = MagicMock()
        mocked_diverge = MagicMock(return_value=(False, False))

        repo = Repository(mocked_repo)
        repo.diverge = mocked_diverge

        assert repo.ahead("origin", "master") is False
        mocked_diverge.assert_called_once_with("origin", "master")

    def test_diverge(self):
        mocked_repo = MagicMock()
        mocked_find = MagicMock()
        mocked_commits = MagicMock()
        mocked_branch_remote = MagicMock(target=1)
        mocked_branch_local = MagicMock(target=2)

        mocked_commits.second_commits = []
        mocked_commits.first_commits = []
        mocked_find.return_value = mocked_commits

        repo = Repository(mocked_repo)
        repo.branches.local.get.return_value = mocked_branch_local
        repo.branches.remote.get.return_value = mocked_branch_remote
        repo.find_diverge_commits = mocked_find

        assert repo.diverge("origin", "master") == (False, False)
        mocked_find.assert_called_once_with(mocked_branch_local, mocked_branch_remote)

    def test_checkout(self):
        mocked_checkout = MagicMock(return_value="done")
        mocked_repo = MagicMock()
        mocked_full_path = MagicMock()
        mocked_index = MagicMock()
        mocked_stats = MagicMock()
        mocked_status = {
            "/": GIT_STATUS_CURRENT,
            "/current/some_path": "another_git_status",
            "/current/another_path": "another_git_status",
        }

        mocked_full_path.return_value = "full_path"
        mocked_repo.checkout = mocked_checkout
        mocked_repo.status.return_value = mocked_status
        mocked_stats.st_mode = "another_mode"

        def contains(self, path):
            if path == "/current/another_path":
                return True
            return False

        mocked_index.__contains__ = contains
        mocked_repo.index = mocked_index

        with patch("gitfs.repository.os") as mocked_os:
            mocked_os.lstat.return_value = mocked_stats

            repo = Repository(mocked_repo)
            repo._full_path = mocked_full_path
            repo.get_git_object_stat = lambda x: {"st_mode": "a_stat"}

            assert repo.checkout("ref", "args") == "done"
            assert mocked_repo.status.call_count == 1
            mocked_checkout.assert_called_once_with("ref", "args")
            mocked_os.unlink.assert_called_once_with("full_path")
            mocked_os.lstat.assert_called_once_with("full_path")
            mocked_os.chmod.assert_called_once_with("full_path", "another_mode")
            mocked_index.add.assert_called_once_with("current/another_path")

    def test_checkout_with_directory_in_status(self):
        mocked_checkout = MagicMock(return_value="done")
        mocked_repo = MagicMock()
        mocked_full_path = MagicMock()
        mocked_index = MagicMock()
        mocked_stats = MagicMock()
        mocked_status = {
            "/": GIT_STATUS_CURRENT,
            "/current/some_path": "another_git_status",
            "/current/another_path": "another_git_status",
        }

        mocked_full_path.return_value = "full_path"
        mocked_repo.checkout = mocked_checkout
        mocked_repo.status.return_value = mocked_status
        mocked_stats.st_mode = "16877"

        def contains(self, path):
            if path == "/current/another_path":
                return True
            return False

        mocked_index.__contains__ = contains
        mocked_repo.index = mocked_index

        mocked_os = MagicMock()
        mocked_rmtree = MagicMock()
        with patch.multiple("gitfs.repository", os=mocked_os, rmtree=mocked_rmtree):
            mocked_os.unlink.side_effect = OSError
            mocked_os.lstat.return_value = mocked_stats

            repo = Repository(mocked_repo)
            repo._full_path = mocked_full_path
            repo.get_git_object_stat = lambda x: {"st_mode": "a_stat"}

            assert repo.checkout("ref", "args") == "done"
            assert mocked_repo.status.call_count == 1
            mocked_checkout.assert_called_once_with("ref", "args")
            mocked_rmtree.assert_called_once_with("full_path", onerror=ANY)
            mocked_os.lstat.assert_called_once_with("full_path")
            mocked_os.chmod.assert_called_once_with("full_path", "16877")
            mocked_index.add.assert_called_once_with("current/another_path")

    def test_git_obj_default_stats_with_invalid_obj(self):
        mocked_repo = MagicMock()
        mocked_git_obj = MagicMock()
        mocked_git_obj.return_value = None

        repo = Repository(mocked_repo)
        repo.get_git_object_type = mocked_git_obj

        assert repo.get_git_object_default_stats("ref", "/") == {
            "st_mode": S_IFDIR | 0o555,
            "st_nlink": 2,
        }
        assert repo.get_git_object_default_stats("ref", "/ups") is None

    def test_git_obj_default_stats_with_valid_obj(self):
        mocked_repo = MagicMock()
        mocked_git_obj = MagicMock()
        mocked_size = MagicMock()

        mocked_git_obj.return_value = GIT_FILEMODE_BLOB
        mocked_size.return_value = 10

        repo = Repository(mocked_repo)
        repo.get_git_object_type = mocked_git_obj
        repo.get_blob_size = mocked_size

        assert repo.get_git_object_default_stats("ref", "/ups") == {
            "st_mode": S_IFREG | 0o444,
            "st_size": 10,
        }
        mocked_size.assert_called_once_with("ref", "/ups")
        mocked_git_obj.assert_called_once_with("ref", "/ups")

    def test_full_path(self):
        mocked_repo = MagicMock()
        mocked_repo.workdir = "workdir"

        repo = Repository(mocked_repo)
        assert repo._full_path("/partial") == "workdir/partial"
