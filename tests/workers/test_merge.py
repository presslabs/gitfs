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

    def test_on_idle_with_commits_and_merges(self):
        mocked_want_to_merge = MagicMock()
        mocked_commit = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)
        worker.commit = mocked_commit

        commits, merges = worker.on_idle("commits", "merges")

        mocked_commit.assert_called_once_with("commits")
        assert mocked_want_to_merge.set.call_count == 1
        assert commits == []
        assert merges == []

    def test_on_idle_with_merges_and_no_commits(self):
        mocked_want_to_merge = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)

        commits, merges = worker.on_idle(None, "merges")

        assert mocked_want_to_merge.set.call_count == 1
        assert commits is None
        assert merges == []

    def test_on_idle_with_commits_and_no_merges(self):
        mocked_want_to_merge = MagicMock()
        mocked_commit = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)
        worker.commit = mocked_commit

        commits, merges = worker.on_idle("commits", None)

        mocked_commit.assert_called_once_with("commits")
        assert mocked_want_to_merge.set.call_count == 1
        assert commits == []
        assert merges is None

    def test_on_idle_with_no_commits_and_no_merges(self):
        mocked_somebody_is_writing = MagicMock()
        mocked_want_to_merge = MagicMock()
        mocked_merge = MagicMock()
        mocked_push = MagicMock()

        mocked_want_to_merge.is_set.return_value = True
        mocked_somebody_is_writing.is_set.return_value = False

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             somebody_is_writing=mocked_somebody_is_writing,
                             want_to_merge=mocked_want_to_merge)
        worker.merge = mocked_merge
        worker.push = mocked_push

        commits, merges = worker.on_idle(None, None)

        assert mocked_push.call_count == 1
        assert mocked_merge.call_count == 1
        assert mocked_want_to_merge.clear.call_count == 1
        assert commits is None
        assert merges is None

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

    def test_push(self):
        mocked_strategy = MagicMock()
        mocked_repo = MagicMock()
        mocked_fetch = MagicMock(side_effect=ValueError)
        mocked_read_only = MagicMock()
        upstream = "origin"
        branch = "master"

        mocked_read_only.clear.side_effect = ValueError

        worker = MergeWorker("name", "email", "name", "email",
                             strategy=mocked_strategy,
                             repository=mocked_repo,
                             read_only=mocked_read_only,
                             upstream=upstream, branch=branch)
        worker.fetch = mocked_fetch

        with pytest.raises(ValueError):
            worker.push()

        mocked_repo.push.assert_called_once_with("origin", "master")
        assert mocked_fetch.call_count == 1
        assert mocked_read_only.clear.call_count == 1
        assert mocked_read_only.set.call_count == 1

    def test_fetch_when_we_are_ahead(self):
        mocked_strategy = MagicMock()
        mocked_repo = MagicMock()
        mocked_push = MagicMock()
        mocked_queue = MagicMock()

        upstream = "origin"
        branch = "master"

        mocked_repo.fetch.return_value = False
        worker = MergeWorker("name", "email", "name", "email",
                             strategy=mocked_strategy,
                             repository=mocked_repo,
                             merge_queue=mocked_queue,
                             upstream=upstream, branch=branch)
        worker.push = mocked_push

        worker.fetch()

        mocked_repo.fetch.assert_called_once_with(upstream, branch)
        assert mocked_push.call_count == 1

    def test_fetch_when_we_are_behind(self):
        mocked_strategy = MagicMock()
        mocked_repo = MagicMock()
        mocked_push = MagicMock()
        mocked_queue = MagicMock()

        upstream = "origin"
        branch = "master"

        mocked_repo.fetch.return_value = True
        worker = MergeWorker("name", "email", "name", "email",
                             strategy=mocked_strategy,
                             repository=mocked_repo,
                             merge_queue=mocked_queue,
                             upstream=upstream, branch=branch)
        worker.push = mocked_push

        worker.fetch()

        mocked_repo.fetch.assert_called_once_with(upstream, branch)
        mocked_queue.add.assert_called_once_with({'type': 'merge'})
