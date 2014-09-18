from mock import MagicMock, patch, call

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

    def test_reload_branch(self):
        mocked_repo = MagicMock()
        mocked_branch = MagicMock()

        mocked_branch.rename.return_value = "branch"
        mocked_branch.get_object.return_value = "remote_commit"
        mocked_repo.lookup_branch.return_value = mocked_branch
        mocked_repo.lookup_reference.return_value = "ref"

        mine = AcceptMine(mocked_repo)
        mine.reload_branch("branch", "origin")

    def test_solve_conflicts_we_deleted_the_file(self):
        mocked_repo = MagicMock()
        mocked_file = MagicMock()

        mocked_file.path = "simple_path"

        def conflicts():
            yield None, mocked_file, None

        mine = AcceptMine(mocked_repo)
        mine.solve_conflicts(conflicts())

        mocked_repo.index.remove.assert_called_once_with("simple_path")

    def test_solve_conflicts_they_deleted_the_file(self):
        mocked_repo = MagicMock()
        mocked_file = MagicMock()

        mocked_file.path = "simple_path"

        def conflicts():
            yield None, None, mocked_file

        mine = AcceptMine(mocked_repo)
        mine.solve_conflicts(conflicts())

        mocked_repo.index.add.assert_called_once_with("simple_path")

    def test_solve_conflicts_both_update_a_file(self):
        mocked_repo = MagicMock()
        mocked_theirs = MagicMock()
        mocked_ours = MagicMock()
        mocked_full = MagicMock()

        mocked_ours.id = "id"
        mocked_ours.path = "path"
        mocked_repo.get().data = "data"
        mocked_full.return_value = "full_path"

        def conflicts():
            yield None, mocked_theirs, mocked_ours

        mock_path = 'gitfs.merges.accept_mine.open'
        with patch(mock_path, create=True) as mocked_open:
            mocked_file = MagicMock(spec=file)
            mocked_open.return_value = mocked_file

            mine = AcceptMine(mocked_repo)
            mine._full_path = mocked_full

            mine.solve_conflicts(conflicts())

            mocked_full.assert_called_once_with("path")
            mocked_open.assert_called_once_with("full_path", "w")
            mocked_repo.get.has_calls([call("id")])
            mocked_open().__enter__().write.assert_called_once_with("data")
            mocked_repo.index.add.assert_called_once_with("path")
