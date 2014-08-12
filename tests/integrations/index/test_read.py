import os

from tests.integrations.base import BaseTest


class TestReadIndexView(BaseTest):
    def test_listdirs(self):
        assert os.listdir(self.mount_path) == ['current', 'history']
