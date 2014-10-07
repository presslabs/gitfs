from collections import namedtuple

from mock import MagicMock, patch, call

from pygit2 import GIT_BRANCH_LOCAL, GIT_BRANCH_REMOTE, GIT_CHECKOUT_FORCE

from gitfs.merges.accept_mine import AcceptMine


Commit = namedtuple("Commit", ["hex", "message", "id"])


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

    def test_create_remote_copy(self):
        mocked_repo = MagicMock()
        mocked_branch = MagicMock()

        mocked_branch.get_object.return_value = "remote_commit"
        mocked_repo.lookup_branch.return_value = mocked_branch
        mocked_repo.lookup_reference.return_value = "ref"
        mocked_repo.create_branch.return_value = "branch"

        mine = AcceptMine(mocked_repo)
        assert mine._create_remote_copy("old_branch", "upstream",
                                        "new_branch") == "branch"

        reference = "%s/%s" % ("upstream", "old_branch")
        mocked_repo.lookup_branch.assert_called_once_with(reference,
                                                          GIT_BRANCH_REMOTE)
        assert mocked_branch.get_object.call_count == 1
        mocked_repo.create_branch.assert_called_once_with("new_branch",
                                                          "remote_commit")
        mocked_repo.checkout.has_calls([call("ref",
                                             strategy=GIT_CHECKOUT_FORCE)])

        asserted_ref = "refs/heads/new_branch"
        mocked_repo.lookup_reference.assert_called_once_with(asserted_ref)

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

    def test_full_path(self):
        mocked_repo = MagicMock()

        with patch('gitfs.merges.accept_mine.os') as mocked_os:
            mocked_os.path.join.return_value = "full_path"

            mine = AcceptMine(mocked_repo)
            mine.repo_path = "repo_path"

            assert mine._full_path("/partial") == "full_path"
            mocked_os.path.join.assert_called_once_with("repo_path", "partial")

    def test_merging_strategy(self):
        mocked_repo = MagicMock()
        mocked_copy = MagicMock()
        mocked_remote_copy = MagicMock()
        mocked_reload = MagicMock()
        mocked_diverge = MagicMock()
        mocked_solve = MagicMock()
        mocked_ref = MagicMock()
        mocked_find_commits = MagicMock()

        mocked_ref.target = "target"
        mocked_diverge.first_commits = [Commit(1, "message", 1)]
        mocked_repo.index.conflicts = "conflicts"
        mocked_repo.lookup_reference.return_value = mocked_ref
        mocked_repo.commit.return_value = "new_commit"
        mocked_repo.find_diverge_commits = mocked_find_commits
        mocked_reload.return_value = "reload"
        mocked_find_commits.return_value = mocked_diverge
        mocked_copy.return_value = "local_copy"
        mocked_remote_copy.return_value = "remote_copy"

        mine = AcceptMine(mocked_repo, author="author", commiter="commiter")

        mine._create_local_copy = mocked_copy
        mine._create_remote_copy = mocked_remote_copy
        mine.reload_branch = mocked_reload
        mine.solve_conflicts = mocked_solve

        mine.__call__("local_branch", "remote_branch", "upstream")

        mocked_copy.assert_called_once_with("local_branch", "merging_local")
        mocked_remote_copy.assert_called_once_with("remote_branch", "upstream",
                                                   "merging_remote")
        mocked_find_commits.assert_called_once_with("local_copy",
                                                    "remote_copy")
        mocked_repo.checkout.has_calls([call("refs/heads/local_branch",
                                             strategy=GIT_CHECKOUT_FORCE)])
        mocked_repo.merge.assert_called_once_with(1)
        mocked_solve.asssert_called_once_with(mocked_repo.index.conflicts)

        asserted_calls = [call("refs/heads/local_branch"),
                          call("refs/heads/merging_local")]
        mocked_repo.lookup_reference.has_calls(asserted_calls)
        mocked_repo.commit.asserted_called_once_with("merging: message",
                                                     "author", "commiter",
                                                     mocked_ref, ["target", 1])
        mocked_repo.create_reference.called_once_with(mocked_ref, "new_commit",
                                                      force=True)
        assert mocked_repo.state_cleanup.call_count == 1
        assert mocked_ref.delete.call_count == 2
