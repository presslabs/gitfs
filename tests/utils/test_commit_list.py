from mock import MagicMock

from gitfs.utils.commits import CommitsList


class TestCommitList(object):
    def test_contains(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        assert mocked_commit not in commit_list

    def test_index(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        commit_list.append(mocked_commit)
        assert commit_list.index(mocked_commit) == 0

    def test_getitem(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        commit_list.append(mocked_commit)
        assert commit_list[:1].hashes == ["hexish"]
        assert commit_list[:1].commits == [mocked_commit]
