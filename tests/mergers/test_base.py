from mock import MagicMock

from gitfs.merges.base import Merger


class TestBaseMerger(object):
    def test_peasant_work(self):
        mocked_repo = MagicMock()

        merger = Merger(mocked_repo, kwarg="arg")
        assert merger.kwarg == "arg"
