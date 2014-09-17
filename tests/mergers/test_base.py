from collections import namedtuple

from mock import MagicMock

from gitfs.merges.base import Merger


Commit = namedtuple("Commit", "hex")


class TestBaseMerger(object):
    def test_find_diverge_commits_first_from_second(self):
        mocked_repo = MagicMock()

        def walker():
            first_branch = [Commit(1), Commit(2), Commit(3), Commit(4)]
            second_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        mocked_repo.walk_branches.return_value = walker()

        merger = Merger(mocked_repo)
        result = merger.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_find_diverge_commits_second_from_first(self):
        mocked_repo = MagicMock()

        def walker():
            first_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]
            second_branch = [Commit(1), Commit(2), Commit(3), Commit(4)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        mocked_repo.walk_branches.return_value = walker()

        merger = Merger(mocked_repo)
        result = merger.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_find_diverge_commits_common_commit(self):
        mocked_repo = MagicMock()

        def walker():
            first_branch = [Commit(5), Commit(6), Commit(2), Commit(3)]
            second_branch = [Commit(1), Commit(0), Commit(2), Commit(3)]

            for index, commit in enumerate(first_branch):
                yield (commit, second_branch[index])

        mocked_repo.walk_branches.return_value = walker()

        merger = Merger(mocked_repo)
        result = merger.find_diverge_commits("first_branch", "second_branch")
        assert result.common_parent == Commit(2)

    def test_peasant_work(self):
        mocked_repo = MagicMock()

        merger = Merger(mocked_repo, kwarg="arg")
        assert merger.kwarg == "arg"
