import time

import pytest
from mock import MagicMock, patch, call
from pygit2 import GIT_BRANCH_REMOTE, GIT_SORT_TIME

from gitfs.utils import Repository
from .base import RepositoryBaseTest


"""
TODO (still need to be tested):
    * commit
    * get_blob_data
    * get_blob_size
    * get_git_object
    * get_git_object_type
"""


class TestRepository(RepositoryBaseTest):

    def test_push(self):
        mocked_repo = MagicMock()
        mocked_remote = MagicMock()
        mocked_remote.name = "origin"
        mocked_repo.remotes = [mocked_remote]

        repo = Repository(mocked_repo)
        repo.push("origin", "master")

        mocked_remote.push.assert_called_once_with("refs/heads/master")

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

        repo = Repository(mocked_repo)
        behind = repo.fetch("origin", "master")

        assert behind is True
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

        with patch('gitfs.utils.repository.Signature') as mocked_signature:
            mocked_signature.return_value = "signature"

            repo = Repository(mocked_repo)
            commit = repo.commit("message", author, commiter)

            assert commit == "commit"
            assert mocked_repo.status.call_count == 1
            assert mocked_repo.index.write_tree.call_count == 1
            assert mocked_repo.index.write.call_count == 1

            mocked_signature.has_calls([call(*author), call(*commiter)])
            mocked_repo.revparse_single.assert_called_once_with("HEAD")
            mocked_repo.create_commit.assert_called_once_with("HEAD",
                                                              "signature",
                                                              "signature",
                                                              "message",
                                                              "tree", [1])

    def test_commit_with_nothing_to_commit(self):
        mocked_repo = MagicMock()
        mocked_repo.status.return_value = False

        author = ("author_1", "author_2")
        commiter = ("commiter_1", "commiter_2")

        repo = Repository(mocked_repo)
        commit = repo.commit("message", author, commiter)

        assert commit is None

    def test_clone(self):
        mocked_repo = MagicMock()

        remote_url = "git@github.com:test/test.git"
        path = "/path/to/repo"

        with patch('gitfs.utils.repository.clone_repository') as mocked_clone:
            mocked_clone.return_value = mocked_repo

            Repository.clone(remote_url, path)

            mocked_clone.assert_called_once_with(remote_url, path,
                                                 checkout_branch=None)
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

        ref = "%s/%s" % (upstream, branch)
        mocked_repo.lookup_branch.assert_called_once_with(ref,
                                                          GIT_BRANCH_REMOTE)

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

            def next(self):
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

        def mocked_walk(target):
            return BranchWalker() if target == "first" else BranchWalker(2)
        mocked_repo.walk = mocked_walk

        repo = Repository(mocked_repo)

        counter_1 = 1
        counter_2 = 1
        branches = (MagicMock(target='first'), MagicMock(target='second'))
        for commit_1, commit_2 in repo.walk_branches(GIT_SORT_TIME, *branches):
            assert commit_1 == counter_1
            assert commit_2 == counter_2

            if counter_2 < 9:
                counter_2 += 2
            counter_1 += 1

    def test_get_commits_by_dates(self):
        mocked_repo = MagicMock()
        commits = {
            'now': [1, 2, 3]
        }

        repo = Repository(mocked_repo, commits)
        assert repo.get_commits_by_date('now') == ['1', '2', '3']

    def test_get_commit_dates(self):
        mocked_repo = MagicMock()
        commits = {
            'now': [1, 2, 3]
        }

        repo = Repository(mocked_repo, commits)
        assert repo.get_commit_dates() == ['now']
