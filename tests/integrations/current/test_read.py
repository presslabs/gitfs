import os

from tests.integrations.base import BaseTest


class TestReadCurrentView(BaseTest):
    def test_listdirs(self):
        dirs = set(os.listdir("%s/current" % self.mount_path))
        assert dirs== set(['testing', 'me'])

    def test_read_from_a_file(self):
        with open("%s/current/testing" % self.mount_path) as f:
            assert f.read() == "just testing around here\n"
