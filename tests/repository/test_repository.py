import __builtin__
from pytest import raises
from mock import MagicMock, Mock, PropertyMock, patch, call
from pygit2 import (GIT_CHECKOUT_SAFE_CREATE, GIT_CHECKOUT_FORCE, GIT_SORT_TIME,
                    GIT_BRANCH_REMOTE, Repository as _Repository)

from .base import RepositoryBaseTest
from gitfs.utils import Repository


"""
TODO (still need to be tested):
    * commit
    * get_blob_data
    * get_blob_size
    * get_git_object
    * get_git_object_type
"""
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
                            _Repository=MagicMock(),
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
            call('refs/heads/%s' % branch, mocked_returned_commit, force=True)]
        mocked_create_reference.has_calls(mocked_create_reference_calls)

    def test_get_remote(self):
        remote1 = MagicMock()
        remote1.name = 'remote1'
        remote2 = MagicMock()
        remote2.name = 'remote2'

        with patch('gitfs.utils.repository.Repository.remotes',
                   new_callable=PropertyMock) as mocked_remotes:
            mocked_remotes.return_value = [remote1, remote2]
            repo = self._get_repository()
            remote = repo.get_remote('remote2')
            assert remote.name == 'remote2'

            with raises(ValueError):
                remote = repo.get_remote('unavailable_remote')

    def test_get_commit_dates(self):
        mocked_commit1 = MagicMock()
        mocked_commit1.commit_time = '1408626757'
        mocked_commit2 = MagicMock()
        mocked_commit2.commit_time = '1408626757'

        mocked_walk = MagicMock()
        mocked_walk.return_value = [mocked_commit1, mocked_commit2]

        mocked_lookup_reference = MagicMock()
        mocked_lookup_reference.return_value.resolve.return_value.target = 'target'

        mocked_datetime = MagicMock()

        mocked_commit_date1 = MagicMock()
        mocked_commit_date1.strftime.return_value = mocked_commit1.commit_time

        mocked_commit_date2 = MagicMock()
        mocked_commit_date2.strftime.return_value = mocked_commit2.commit_time

        mocked_datetime.fromtimestamp.return_value.date.side_effect = [
            mocked_commit_date1, mocked_commit_date2]

        with patch.multiple('gitfs.utils.repository',
                            _Repository=MagicMock(),
                            datetime=mocked_datetime):
            repo = self._get_repository()
            repo.walk = mocked_walk
            repo.lookup_reference = mocked_lookup_reference

            commit_dates = repo.get_commit_dates()

            #assert mocked_lookup_reference.mock_calls == [call('HEAD'),
                                                          #call().resolve()]

            #assert mocked_walk.mock_calls == [call('target', GIT_SORT_TIME)]
            #datetime_calls = [call.fromtimestamp('1408626757'),
                              #call.fromtimestamp().date()]
            #mocked_datetime.assert_has_calls(datetime_calls)
            #mocked_commit_date.assert_has_calls([call.strftime('%Y-%m-%d')])
