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
        mocked_repo.get_commit_dates.return_value = ['/']
        with patch('gitfs.views.history.lru_cache') as mocked_cache:
            mocked_cache.__call__ = lambda f: f

            history = HistoryView(repo=mocked_repo, uid=1, gid=1,
                                  mount_time="now")
            history._get_first_commit_time = mocked_first
            history._get_last_commit_time = mocked_last

            result = history.getattr("/", 1)
            asserted_result = {
                'st_uid': 1,
                'st_gid': 1,
                'st_ctime': "tomorrow",
                'st_mtime': "tomorrow",
                'st_nlink': 2,
                'st_mode': S_IFDIR | 0555,
            }
            assert asserted_result == result

    def test_getattr_with_incorrect_path(self):
        mocked_repo = MagicMock()

        mocked_repo.get_commit_dates.return_value = ['/path']

        with patch('gitfs.views.history.lru_cache') as mocked_cache:
            mocked_cache.__call__ = lambda f: f

            history = HistoryView(repo=mocked_repo, uid=1, gid=1,
                                  mount_time="now")

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
