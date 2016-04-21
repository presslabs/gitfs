# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
        assert sorted(cache.keys()) == ['2014-09-19', '2014-09-20']
        asserted_time = datetime.fromtimestamp(mocked_commit.commit_time)
        asserted_time = "{}-{}-{}".format(asserted_time.hour, asserted_time.minute,
                                          asserted_time.second)
        assert repr(cache['2014-09-19']) == '[%s-1111111111]' % asserted_time
        del cache['2014-09-20']
        for commit_date in cache:
            assert commit_date == '2014-09-19'

        mocked_repo.lookup_reference.has_calls([call("HEAD")])
        mocked_repo.walk.assert_called_once_with("head", GIT_SORT_TIME)
        assert mocked_repo.lookup_reference().resolve.call_count == 2
