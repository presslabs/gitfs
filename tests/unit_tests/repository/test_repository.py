import __builtin__
from pytest import fail
from mock import MagicMock, patch, call
from pygit2 import GIT_CHECKOUT_SAFE_CREATE

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

    #def test_pull(self):
        #mocked_remote = MagicMock()
        #mocked_branch = MagicMock()
        #mocked_get_remote = MagicMock(return_value=mocked_remote)
        #mocked_lookup_branch = MagicMock(return_value=mocked_branch)
        #mocked_merge = MagicMock()
        #mocked_create_reference = MagicMock()
        #mocked_commit = MagicMock()

        #remote = "origin"
        #branch = "master"

        #repo = self._get_repository()
        #repo.get_remote = mocked_get_remote
        #repo.lookup_branch = mocked_lookup_branch
        #repo.pull(remote, branch)

