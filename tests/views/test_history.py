# Copyright 2014-2016 Presslabs SRL
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


from stat import S_IFDIR

import pytest
from mock import patch, MagicMock

from fuse import FuseOSError

from gitfs.views.history import HistoryView


class TestHistory(object):
    def test_getattr_with_correct_path(self):
        mocked_repo = MagicMock()
        mocked_first = MagicMock()
        mocked_last = MagicMock()

        mocked_first.return_value = "tomorrow"
        mocked_last.return_value = "tomorrow"
        mocked_repo.get_commit_dates.return_value = ["/"]
        with patch("gitfs.views.history.lru_cache") as mocked_cache:
            mocked_cache.__call__ = lambda f: f

            history = HistoryView(repo=mocked_repo, uid=1, gid=1, mount_time="now")
            history._get_first_commit_time = mocked_first
            history._get_last_commit_time = mocked_last

            result = history.getattr("/", 1)
            asserted_result = {
                "st_uid": 1,
                "st_gid": 1,
                "st_ctime": "tomorrow",
                "st_mtime": "tomorrow",
                "st_nlink": 2,
                "st_mode": S_IFDIR | 0o555,
            }
            assert asserted_result == result

    def test_getattr_with_incorrect_path(self):
        mocked_repo = MagicMock()

        mocked_repo.get_commit_dates.return_value = ["/path"]

        with patch("gitfs.views.history.lru_cache") as mocked_cache:
            mocked_cache.__call__ = lambda f: f

            history = HistoryView(repo=mocked_repo, uid=1, gid=1, mount_time="now")

            with pytest.raises(FuseOSError):
                history.getattr("/not-ok", 1)

    def test_access_with_invalid_path_and_no_date(self):
        history = HistoryView()

        with pytest.raises(FuseOSError):
            history.access("path", "mode")

    def test_access_with_valid_path_and_no_date(self):
        history = HistoryView()
        assert history.access("/", "mode") == 0

    def test_access_with_date_and_valid_path(self):
        mocked_repo = MagicMock()
        mocked_repo.get_commit_dates.return_value = ["tomorrow"]

        history = HistoryView(repo=mocked_repo)
        history.date = "now"

        with pytest.raises(FuseOSError):
            history.access("/", "mode")

    def test_access_with_date_and_invalid_path(self):
        mocked_repo = MagicMock()
        mocked_repo.get_commits_by_date.return_value = ["tomorrow"]

        history = HistoryView(repo=mocked_repo)
        history.date = "now"

        with pytest.raises(FuseOSError):
            history.access("/non", "mode")

        mocked_repo.get_commits_by_date.assert_called_once_with("now")

    def test_readdir_without_date(self):
        mocked_repo = MagicMock()
        mocked_repo.get_commit_dates.return_value = ["tomorrow"]

        history = HistoryView(repo=mocked_repo)

        asserted_dirs = [".", "..", "tomorrow"]
        dirs = [entry for entry in history.readdir("path", 0)]
        assert dirs == asserted_dirs
        assert mocked_repo.get_commit_dates.call_count == 1

    def test_readdir_with_date(self):
        mocked_repo = MagicMock()
        mocked_repo.get_commits_by_date.return_value = ["tomorrow"]

        history = HistoryView(repo=mocked_repo)
        history.date = "now"

        asserted_dirs = [".", "..", "tomorrow"]
        dirs = [entry for entry in history.readdir("path", 0)]
        assert dirs == asserted_dirs
        mocked_repo.get_commits_by_date.assert_called_once_with("now")

    def test_get_commit_time_without_date(self):
        mocked_repo = MagicMock()

        with patch("gitfs.views.history.time") as mocked_time:
            mocked_time.time.return_value = "1"

            history = HistoryView(repo=mocked_repo)
            assert history._get_commit_time(0) == 1

    def test_get_commit_time_with_valid_date(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.timestamp = 0
        mocked_repo.commits = {"now": [mocked_commit]}

        with patch("gitfs.views.history.time") as mocked_time:
            mocked_time.time.return_value = "1"

            history = HistoryView(repo=mocked_repo)
            history.date = "now"

            assert history._get_commit_time(0) == 0

    def test_get_commit_time_with_invalid_date(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()

        mocked_commit.timestamp = 1
        mocked_repo.commits = {"now": [mocked_commit]}

        with patch("gitfs.views.history.time") as mocked_time:
            mocked_time.time.return_value = "1"

            history = HistoryView(repo=mocked_repo)
            history.date = "not-now"

            assert history._get_commit_time(0) == 1

    def test_last_commit_time(self):
        mocked_repo = MagicMock()

        mocked_commit_time = MagicMock()
        mocked_commit_time.return_value = 1

        history = HistoryView(repo=mocked_repo)
        history._get_commit_time = mocked_commit_time

        assert history._get_last_commit_time() == 1
        mocked_commit_time.assert_called_once_with(-1)

    def test_first_commit_time(self):
        mocked_repo = MagicMock()

        mocked_commit_time = MagicMock()
        mocked_commit_time.return_value = 1

        history = HistoryView(repo=mocked_repo)
        history._get_commit_time = mocked_commit_time

        assert history._get_first_commit_time() == 1
        mocked_commit_time.assert_called_once_with(0)
