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

    def test_iter(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        commit_list.append(mocked_commit)
        commit_list.append(mocked_commit)

        for commit in commit_list:
            assert commit == mocked_commit

    def test_repr(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        commit_list.append(mocked_commit)

        assert repr(commit_list) == repr([mocked_commit])

    def test_len(self):
        mocked_commit = MagicMock()
        mocked_commit.hex = "hexish"

        commit_list = CommitsList()
        commit_list.append(mocked_commit)

        assert len(commit_list) == 1
