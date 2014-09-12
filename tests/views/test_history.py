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
