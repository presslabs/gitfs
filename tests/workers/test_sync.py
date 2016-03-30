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
from _pygit2 import GitError

from mock import MagicMock, patch, call
from six.moves.queue import Empty
import pygit2
import pytest

from gitfs.worker.sync import SyncWorker


class TestSyncWorker(object):
    def test_work(self):
        mocked_queue = MagicMock()
        mocked_idle = MagicMock(side_effect=ValueError)

        mocked_queue.get.side_effect = Empty()

        worker = SyncWorker("name", "email", "name", "email",
                            strategy="strategy", commit_queue=mocked_queue)
        worker.on_idle = mocked_idle
        worker.timeout = 1
        worker.min_idle_times = 1

        with pytest.raises(ValueError):
            worker.work()

        mocked_queue.get.assert_called_once_with(timeout=1, block=True)
        assert mocked_idle.call_count == 1

    def test_on_idle_with_commits_and_merges(self):
        mocked_sync = MagicMock()
        mocked_syncing = MagicMock()
        mocked_commit = MagicMock()

        mocked_syncing.is_set.return_value = False

        with patch.multiple("gitfs.worker.sync", syncing=mocked_syncing,
                            writers=MagicMock(value=0)):
            worker = SyncWorker("name", "email", "name", "email",
                                strategy="strategy")
            worker.commits = "commits"
            worker.commit = mocked_commit
            worker.sync = mocked_sync

            commits = worker.on_idle()

            mocked_commit.assert_called_once_with("commits")
            assert mocked_syncing.set.call_count == 1
            assert mocked_sync.call_count == 1
            assert commits is None

    def test_merge(self):
        mocked_strategy = MagicMock()
        mocked_repo = MagicMock()
        upstream = "origin"
        branch = "master"

        worker = SyncWorker("name", "email", "name", "email",
                            strategy=mocked_strategy,
                            repository=mocked_repo,
                            upstream=upstream, branch=branch)
        worker.merge()

        mocked_strategy.assert_called_once_with(branch, branch, upstream)
        assert mocked_repo.commits.update.call_count == 1

    def test_sync(self):
        upstream = "origin"
        branch = "master"
        credentials = "credentials"
        mocked_repo = MagicMock()
        mocked_merge = MagicMock()
        mocked_sync_done = MagicMock()
        mocked_syncing = MagicMock()
        mocked_push_successful = MagicMock()
        mocked_fetch = MagicMock()
        mocked_strategy = MagicMock()

        mocked_repo.behind = True
        mocked_push_successful.set.side_effect = ValueError

        with patch.multiple('gitfs.worker.sync', sync_done=mocked_sync_done,
                            syncing=mocked_syncing,
                            push_successful=mocked_push_successful,
                            fetch=mocked_fetch):
            worker = SyncWorker("name", "email", "name", "email",
                                repository=mocked_repo,
                                strategy=mocked_strategy,
                                credentials=credentials,
                                upstream=upstream, branch=branch)
            worker.merge = mocked_merge

            worker.sync()

            assert mocked_syncing.clear.call_count == 1
            assert mocked_push_successful.clear.call_count == 1
            assert mocked_sync_done.clear.call_count == 1
            assert mocked_sync_done.set.call_count == 1
            assert mocked_fetch.set.call_count == 1
            assert mocked_push_successful.set.call_count == 1
            assert mocked_repo.behind is False
            mocked_repo.push.assert_called_once_with(upstream, branch,
                                                     credentials)

    def test_sync_with_push_conflict(self):
        upstream = "origin"
        branch = "master"
        credentials = "credentials"
        mocked_repo = MagicMock()
        mocked_merge = MagicMock()
        mocked_sync_done = MagicMock()
        mocked_syncing = MagicMock()
        mocked_push_successful = MagicMock()
        mocked_fetch = MagicMock()
        mocked_strategy = MagicMock()

        mocked_repo.behind = True
        mocked_repo.ahead = MagicMock(1)
        mocked_repo.push.side_effect = [GitError("Mocked error"), None]

        with patch.multiple('gitfs.worker.sync', sync_done=mocked_sync_done,
                            syncing=mocked_syncing,
                            push_successful=mocked_push_successful,
                            fetch=mocked_fetch):
            worker = SyncWorker("name", "email", "name", "email",
                                repository=mocked_repo,
                                strategy=mocked_strategy,
                                credentials=credentials,
                                upstream=upstream, branch=branch)
            worker.merge = mocked_merge

            while not worker.sync():
                pass

            assert mocked_syncing.clear.call_count == 1
            assert mocked_push_successful.clear.call_count == 1
            assert mocked_sync_done.clear.call_count == 2
            assert mocked_sync_done.set.call_count == 1
            assert mocked_fetch.set.call_count == 1
            assert mocked_push_successful.set.call_count == 1
            assert mocked_repo.behind is False
            assert mocked_repo.ahead.call_count == 2

            mocked_repo.push.assert_has_calls([call(upstream, branch, credentials),
                                               call(upstream, branch, credentials)])

    def test_commit_with_just_one_job(self):
        mocked_repo = MagicMock()

        message = 'just a simple message'
        jobs = [{'params': {'message': message}}]
        author = ("name", "email")

        worker = SyncWorker(author[0], author[1], author[0], author[1],
                            strategy="strategy",
                            repository=mocked_repo)
        worker.commit(jobs)

        mocked_repo.commit.assert_called_once_with(message, author, author)
        assert mocked_repo.commits.update.call_count == 1

        strategy = pygit2.GIT_CHECKOUT_FORCE
        mocked_repo.checkout_head.assert_called_once_with(strategy=strategy)

    def test_commit_with_more_than_one_job(self):
        mocked_repo = MagicMock()

        message = 'just a simple message'
        jobs = [{'params': {'message': message, 'add': ['path1', 'path2'],
                            'remove': []}},
                {'params': {'message': message, 'remove': ['path2'],
                            'add': []}}]
        author = ("name", "email")

        worker = SyncWorker(author[0], author[1], author[0], author[1],
                            strategy="strategy",
                            repository=mocked_repo)
        worker.commit(jobs)

        asserted_message = "Update 2 items"
        mocked_repo.commit.assert_called_once_with(asserted_message, author,
                                                   author)
        assert mocked_repo.commits.update.call_count == 1

        strategy = pygit2.GIT_CHECKOUT_FORCE
        mocked_repo.checkout_head.assert_called_once_with(strategy=strategy)

    def test_switch_to_idle_mode(self):
        mocked_queue = MagicMock()
        mocked_idle = MagicMock(side_effect=ValueError)
        mocked_idle_event = MagicMock()

        mocked_queue.get.side_effect = Empty()

        with patch.multiple('gitfs.worker.sync', idle=mocked_idle_event):
            worker = SyncWorker("name", "email", "name", "email",
                                strategy="strategy", commit_queue=mocked_queue)
            worker.on_idle = mocked_idle
            worker.timeout = 1
            worker.min_idle_times = -1

            with pytest.raises(ValueError):
                worker.work()

            mocked_queue.get.assert_called_once_with(timeout=1, block=True)
            assert mocked_idle_event.set.call_count == 1
            assert mocked_idle.call_count == 1
