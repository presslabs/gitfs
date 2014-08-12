import os

from tests.integrations.base import BaseTest


class TestReadCurrentView(BaseTest):
    def test_listdirs(self):
        assert os.listdir("%s/current" % self.mount_path) == ['testing', 'me']

    def test_read_from_a_file(self):
        with open("%s/current/testing" % self.mount_path) as f:
            assert f.read() == "just testing around here\n"
