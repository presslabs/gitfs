from threading import Event

import pytest
from mock import patch, MagicMock

from gitfs.worker.fetch import FetchWorker


class TestFetchWorker(object):
    def test_run(self):
        mocked_peasant = MagicMock()
        mocked_time = MagicMock()
        mocked_fetch = MagicMock(side_effect=ValueError)

        with patch.multiple('gitfs.worker.fetch', Peasant=mocked_peasant,
                            time=mocked_time):
            worker = FetchWorker()
            worker.fetch = mocked_fetch
            worker.timeout = 5

            with pytest.raises(ValueError):
                worker.run()

            mocked_time.sleep.asserted_called_once_with(5)
            assert mocked_fetch.call_count == 1

    def test_fetch_we_are_not_behind(self):
        mocked_read_only = MagicMock()
        mocked_fetching = MagicMock()
        mocked_repo = MagicMock()
        mocked_queue = MagicMock()

        mocked_repo.fetch.return_value = False

        worker = FetchWorker(read_only=mocked_read_only,
                             fetching=mocked_fetching,
                             repository=mocked_repo,
                             pushing=Event(),
                             merge_queue=mocked_queue,
                             upstream="origin",
                             branch="master")
        worker.fetch()

        assert mocked_read_only.clear.call_count == 1
        assert mocked_fetching.clear.call_count == 1
        assert mocked_fetching.set.call_count == 1
        mocked_repo.fetch.assert_called_once_with("origin", "master")

    def test_fetch_we_are_behind(self):
        mocked_read_only = MagicMock()
        mocked_repo = MagicMock()
        mocked_queue = MagicMock()
        mocked_fetching = MagicMock()

        mocked_repo.fetch.return_value = True

        worker = FetchWorker(read_only=mocked_read_only,
                             fetching=mocked_fetching,
                             repository=mocked_repo,
                             merge_queue=mocked_queue,
                             pushing=Event(),
                             upstream="origin",
                             branch="master")
        worker.fetch()

        assert mocked_read_only.clear.call_count == 1
        assert mocked_fetching.clear.call_count == 1
        assert mocked_fetching.set.call_count == 1
        mocked_repo.fetch.assert_called_once_with("origin", "master")
        mocked_queue.add.assert_called_once_with({'type': 'merge'})

    def test_fetch_remote_is_down(self):
        mocked_read_only = MagicMock()
        mocked_repo = MagicMock()
        mocked_queue = MagicMock()
        mocked_fetching = MagicMock()

        mocked_repo.fetch = MagicMock(side_effect=ValueError)

        worker = FetchWorker(read_only=mocked_read_only,
                             fetching=mocked_fetching,
                             repository=mocked_repo,
                             pushing=Event(),
                             merge_queue=mocked_queue,
                             upstream="origin",
                             branch="master")
        worker.fetch()

        assert mocked_read_only.set.call_count == 1
        assert mocked_fetching.clear.call_count == 1
        assert mocked_fetching.set.call_count == 1
        mocked_repo.fetch.assert_called_once_with("origin", "master")
