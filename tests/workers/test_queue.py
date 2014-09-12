import pytest
from mock import patch, MagicMock

from gitfs.worker.queue import BaseQueue


class TestBaseQueue(object):
    def test_commit(self):
        queue = BaseQueue()

        with pytest.raises(Exception):
            queue.commit()

    def test_get(self):
        mocked_queue = MagicMock()
        mocked_queue.get.return_value = "get"

        with patch('gitfs.worker.queue.Queue') as mocked_queue_module:
            mocked_queue_module.return_value = mocked_queue

            queue = BaseQueue()
            assert queue.get("args", arg="kwarg") == "get"
            mocked_queue.get.assert_called_once_with("args", arg="kwarg")
