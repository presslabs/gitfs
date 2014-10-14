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


import pytest
from mock import patch, MagicMock

from gitfs.worker.commit_queue import BaseQueue, CommitQueue


class TestBaseQueue(object):
    def test_commit(self):
        queue = BaseQueue()

        with pytest.raises(Exception):
            queue.commit()

    def test_get(self):
        mocked_queue = MagicMock()
        mocked_queue.get.return_value = "get"

        with patch('gitfs.worker.commit_queue.Queue') as mocked_queue_module:
            mocked_queue_module.return_value = mocked_queue

            queue = BaseQueue()
            assert queue.get("args", arg="kwarg") == "get"
            mocked_queue.get.assert_called_once_with("args", arg="kwarg")


class TestCommitQueue(object):
    def test_add(self):
        mocked_queue = MagicMock()

        queue = CommitQueue()
        queue.queue = mocked_queue

        queue.add("job")

        mocked_queue.put.assert_called_once_with("job")

    def test_to_list(self):
        queue = CommitQueue()
        assert queue._to_list("a") == ["a"]

    def test_commit_witth_no_message(self):
        queue = CommitQueue()

        with pytest.raises(ValueError):
            queue.commit()

    def test_commit_witth_no_add_and_no_remove(self):
        queue = CommitQueue()

        with pytest.raises(ValueError):
            queue.commit(message="message")

    def test_commit(self):
        mocked_queue = MagicMock()

        queue = CommitQueue()
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
