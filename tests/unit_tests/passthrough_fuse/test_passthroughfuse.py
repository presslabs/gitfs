
from unittest import TestCase
from pytest import fail
from mock import MagicMock, patch

from gitfs.filesystems.passthrough import PassthroughFuse


class TestPassthroughFuse(object):

    def test_full_path(self):
        assert True

