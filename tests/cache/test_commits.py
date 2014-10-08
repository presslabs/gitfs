from datetime import datetime

from mock import MagicMock, call

from pygit2 import GIT_SORT_TIME

from gitfs.cache.commits import Commit, CommitCache


class TestCommit(object):
    def test_commit(self):
        commit = Commit(1, 1, 1)
        new_commit = Commit(2, 2, "21111111111")

        assert new_commit > commit
        assert repr(new_commit) == "2-2111111111"


class TestCommitCache(object):
    def test_cache(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_repo.lookup_reference().resolve().target = "head"
        mocked_repo.walk.return_value = [mocked_commit]
        mocked_commit.commit_time = 1411135000
        mocked_commit.hex = '1111111111'

        cache = CommitCache(mocked_repo)
        cache.update()

        cache['2014-09-20'] = Commit(1, 1, "1111111111")
        assert cache.keys() == ['2014-09-20', '2014-09-19']
        asserted_time = datetime.utcfromtimestamp(mocked_commit.commit_time)
        asserted_time = "%s:%s:%s" % (asserted_time.hour, asserted_time.minute,
                                      asserted_time.second)
        assert repr(cache['2014-09-19']) == '[16:56:40-1111111111]'
        del cache['2014-09-20']
        for commit_date in cache:
            assert commit_date == '2014-09-19'

        mocked_repo.lookup_reference.has_calls([call("HEAD")])
        mocked_repo.walk.assert_called_once_with("head", GIT_SORT_TIME)
        assert mocked_repo.lookup_reference().resolve.call_count == 2
