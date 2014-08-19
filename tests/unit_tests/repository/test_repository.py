import __builtin__
from pytest import fail
from mock import MagicMock, patch, call
from pygit2 import (Repository as _Repository, GIT_CHECKOUT_SAFE_CREATE,
                    GIT_CHECKOUT_FORCE, GIT_BRANCH_REMOTE)

from .base import RepositoryBaseTest
from gitfs.utils import Repository


class TestRepository(RepositoryBaseTest):

    def setup(self):
        super(TestRepository, self).setup()

        def mock_super(*args, **kwargs):
            if args and issubclass(Repository, args[0]):
                return MagicMock()

            return original_super(*args, **kwargs)

        __builtin__.original_super = super
        __builtin__.super = mock_super


    def teardown(self):
        __builtin__.super = __builtin__.original_super
        del __builtin__.original_super

    def _get_repository(self):
        with patch.multiple('gitfs.utils.repository',
                            clone_repository=MagicMock()):
            repo = Repository.clone(self.remote_url, self.repo_path, self.branch)

        return repo

    def test_push(self):
        mocked_remote = MagicMock()
        mocked_get_remote = MagicMock(return_value=mocked_remote)

        remote = "origin"
        branch = "master"

        repo = self._get_repository()
        repo.get_remote = mocked_get_remote
        repo.push(remote, branch)

        mocked_get_remote.assert_called_once_with(remote)
        assert mocked_remote.method_calls == [call.push("refs/heads/%s" % (branch))]

    def test_pull(self):
        remote = "origin"
        branch = "master"
        branch_target = 'test_target'

        mocked_remote = MagicMock()
        mocked_get_remote = MagicMock(return_value=mocked_remote)
        mocked_returned_commit = MagicMock(name='the-commit')
        mocked_commit = MagicMock(return_value=mocked_returned_commit)
        mocked_branch = MagicMock()
        mocked_branch.target = branch_target
        mocked_lookup_branch = MagicMock(return_value=mocked_branch)
        mocked_merge = MagicMock()
        mocked_create_reference = MagicMock()
        mocked_checkout_head = MagicMock()
        mocked_clean_state_files = MagicMock()

        repo = self._get_repository()
        repo.lookup_branch = mocked_lookup_branch
        repo.merge = mocked_merge
        repo.create_reference = mocked_create_reference
        repo.commit = mocked_commit
        repo.checkout_head = mocked_checkout_head
        repo.get_remote = mocked_get_remote
        repo.clean_state_files = mocked_clean_state_files
        repo.pull(remote, branch)

        mocked_get_remote.assert_called_once_with(remote)
        assert mocked_remote.method_calls == [call.fetch()]
        mocked_lookup_branch.assert_called_once_with("%s/%s" % (remote, branch),
                                    GIT_BRANCH_REMOTE)
        mocked_merge.assert_called_once_with(branch_target)
        mocked_checkout_head.assert_called_once_with(GIT_CHECKOUT_FORCE)
        mocked_clean_state_files.assert_called_once_with()
        assert mocked_create_reference.call_count == 2
        mocked_create_reference_calls = [
            call('refs/heads/%s' % branch, branch_target, force=True),
            call('refs/heads/%s' % branch, mocked_returned_commit, force=True),
        ]
        mocked_create_reference.has_calls(mocked_create_reference_calls)

