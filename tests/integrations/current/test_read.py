import os

from tests.integrations.base import BaseTest


class TestReadCurrentView(BaseTest):
    def test_listdirs(self):
        assert os.listdir("%s/current" % self.mount_path) == ['testing', 'me']
