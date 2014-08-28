import __builtin__
from mock import MagicMock, patch, call
from pygit2 import GIT_CHECKOUT_SAFE_CREATE

from .base import RepositoryBaseTest
from gitfs.utils import Repository


class TestRepositoryClone(RepositoryBaseTest):

    def setup(self):
        super(TestRepositoryClone, self).setup()

        def mock_super(*args, **kwargs):
            if args and issubclass(Repository, args[0]):
                return MagicMock()

            return original_super(*args, **kwargs)

        __builtin__.original_super = super
        __builtin__.super = mock_super

    def teardown(self):
        __builtin__.super = __builtin__.original_super
        del __builtin__.original_super

    def test_clone(self):
        mocked_clone_repository = MagicMock()
        mocked_repo = MagicMock()
        mocked_clone_repository.return_value = mocked_repo

        with patch.multiple('gitfs.utils.repository',
                            clone_repository=mocked_clone_repository):

            Repository.clone(self.remote_url, self.repo_path, self.branch)
            mocked_clone_repository.assert_called_once_with(self.remote_url,
                                                            self.repo_path,
                                                            checkout_branch=self.branch)

            calls = [call.checkout_head(GIT_CHECKOUT_SAFE_CREATE)]
            assert mocked_repo.method_calls == calls
