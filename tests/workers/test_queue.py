import pytest
from mock import patch, MagicMock

from gitfs.worker.queue import BaseQueue, MergeQueue


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


class TestMergeQueue(object):
    def test_add(self):
        mocked_queue = MagicMock()

        queue = MergeQueue()
        queue.queue = mocked_queue

        queue.add("job")

        mocked_queue.put.assert_called_once_with("job")

    def test_to_list(self):
        queue = MergeQueue()
        assert queue._to_list("a") == ["a"]

    def test_commit_witth_no_message(self):
        queue = MergeQueue()

        with pytest.raises(ValueError):
            queue.commit()

    def test_commit_witth_no_add_and_no_remove(self):
        queue = MergeQueue()

        with pytest.raises(ValueError):
            queue.commit(message="message")

    def test_commit(self):
        mocked_queue = MagicMock()

        queue = MergeQueue()
        queue.queue = mocked_queue

        queue.commit(message="message", add="add", remove="remove")

        mocked_queue.put.assert_called_once_with({
            'type': 'commit',
            'params': {
                'add': ["add"],
                'message': "message",
                'remove': ["remove"],
            }
        })
