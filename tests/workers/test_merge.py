import pytest
from mock import patch, MagicMock

from gitfs.worker.merge import MergeWorker


class TestMergeWorker(object):
    def test_run(self):
        mocked_queue = MagicMock()
        mocked_idle = MagicMock(side_effect=ValueError)

        mocked_queue.get.side_effect = ValueError()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy", merge_queue=mocked_queue)
        worker.on_idle = mocked_idle
        worker.timeout = 1

        with pytest.raises(ValueError):
            worker.run()

        mocked_queue.get.assert_called_once_with(timeout=1, block=True)
        mocked_idle.assert_called_once_with([], [])
