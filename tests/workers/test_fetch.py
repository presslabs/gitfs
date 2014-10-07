import pytest
from mock import patch, MagicMock

from gitfs.worker.fetch import FetchWorker


class TestFetchWorker(object):
    def test_run(self):
        mocked_peasant = MagicMock()
        mocked_fetch = MagicMock(side_effect=ValueError)
        mocked_fetch_event = MagicMock()

        with patch.multiple('gitfs.worker.fetch', Peasant=mocked_peasant,
                            fetch=mocked_fetch_event):
            worker = FetchWorker()
            worker.fetch = mocked_fetch
            worker.timeout = 5

            with pytest.raises(ValueError):
                worker.run()

            assert mocked_fetch.call_count == 1
            mocked_fetch_event.wait.assert_called_once_with(5)

    def test_fetch_remote_is_down(self):
        mocked_fetch_ok = MagicMock()
        mocked_fetch = MagicMock()
        mocked_repo = MagicMock()

        mocked_repo.fetch = MagicMock(side_effect=ValueError)
        mocked_fetch_ok.set.side_effect = ValueError

        with patch.multiple('gitfs.worker.fetch',
                            fetch_successful=mocked_fetch_ok,
                            fetch=mocked_fetch):
            worker = FetchWorker(repository=mocked_repo,
                                 upstream="origin",
                                 branch="master")
            worker.fetch()

            mocked_repo.fetch.assert_called_once_with("origin", "master")
            assert mocked_fetch_ok.clear.call_count == 1
            assert mocked_fetch.clear.call_count == 1
