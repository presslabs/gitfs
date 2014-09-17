from mock import MagicMock

from pygit2 import GIT_BRANCH_LOCAL

from gitfs.merges.accept_mine import AcceptMine


class TestAcceptMine(object):
    def test_create_local_copy(self):
        mocked_repo = MagicMock()
        mocked_branch = MagicMock()

        mocked_branch.rename.return_value = "branch"
        mocked_repo.lookup_branch.return_value = mocked_branch

        mine = AcceptMine(mocked_repo)
        assert mine._create_local_copy("old_branch", "new_branch") == "branch"

        mocked_repo.lookup_branch.assert_called_once_with("old_branch",
                                                          GIT_BRANCH_LOCAL)
        mocked_branch.rename.assert_called_once_with("new_branch", True)
