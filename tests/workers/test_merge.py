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
from Queue import Empty

import pygit2

import pytest
from mock import MagicMock, patch

from gitfs.worker.merge import MergeWorker


class TestMergeWorker(object):
    def test_run(self):
        mocked_queue = MagicMock()
        mocked_idle = MagicMock(side_effect=ValueError)

        mocked_queue.get.side_effect = Empty()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy", merge_queue=mocked_queue)
        worker.on_idle = mocked_idle
        worker.timeout = 1

        with pytest.raises(ValueError):
            worker.run()

        mocked_queue.get.assert_called_once_with(timeout=1, block=True)
        mocked_idle.assert_called_once_with([])

    def test_on_idle_with_commits_and_merges(self):
        mocked_sync = MagicMock()
        mocked_syncing = MagicMock()
        mocked_commit = MagicMock()

        with patch.multiple("gitfs.worker.merge", syncing=mocked_syncing,
                            writers=0):
            worker = MergeWorker("name", "email", "name", "email",
                                 strategy="strategy")
            worker.commit = mocked_commit
            worker.sync = mocked_sync

            commits = worker.on_idle("commits")

            mocked_commit.assert_called_once_with("commits")
            assert mocked_syncing.set.call_count == 1
            assert mocked_sync.call_count == 1
            assert commits == []

    def test_merge(self):
        mocked_strategy = MagicMock()
        mocked_repo = MagicMock()
        upstream = "origin"
        branch = "master"

        worker = MergeWorker("name", "email", "name", "email",
                             strategy=mocked_strategy,
                             repository=mocked_repo,
                             upstream=upstream, branch=branch)
        worker.merge()

        mocked_strategy.assert_called_once_with(branch, branch, upstream)
        assert mocked_repo.commits.update.call_count == 1

    def test_sync(self):
        upstream = "origin"
        branch = "master"
        mocked_repo = MagicMock()
        mocked_merge = MagicMock()
        mocked_sync_done = MagicMock()
        mocked_syncing = MagicMock()
        mocked_push_successful = MagicMock()
        mocked_fetch = MagicMock()
        mocked_strategy = MagicMock()

        mocked_repo.behind = True
        mocked_push_successful.set.side_effect = ValueError

        with patch.multiple('gitfs.worker.merge', sync_done=mocked_sync_done,
                            syncing=mocked_syncing,
                            push_successful=mocked_push_successful,
                            fetch=mocked_fetch):
            worker = MergeWorker("name", "email", "name", "email",
                                 repository=mocked_repo,
                                 strategy=mocked_strategy,
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
            mocked_repo.push.assert_called_once_with(upstream, branch)

    def test_commit_with_just_one_job(self):
        mocked_repo = MagicMock()

        message = 'just a simple message'
        jobs = [{'params': {'message': message}}]
        author = ("name", "email")

        worker = MergeWorker(author[0], author[1], author[0], author[1],
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

        worker = MergeWorker(author[0], author[1], author[0], author[1],
                             strategy="strategy",
                             repository=mocked_repo)
        worker.commit(jobs)

        asserted_message = "Update 2 items"
        mocked_repo.commit.assert_called_once_with(asserted_message, author,
                                                   author)
        assert mocked_repo.commits.update.call_count == 1

        strategy = pygit2.GIT_CHECKOUT_FORCE
        mocked_repo.checkout_head.assert_called_once_with(strategy=strategy)
