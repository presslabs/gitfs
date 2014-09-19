from gitfs.cache.commits import Commit


class TestCommit(object):
    def test_commit(self):
        commit = Commit(1, 1, 1)
        new_commit = Commit(2, 2, "21111111111")

        assert new_commit > commit
        assert repr(new_commit) == "2-2111111111"


class TestCommitCache(object):
    pass
