import os

from .base import BaseTest


class TestIndexView(BaseTest):
    def test_read_from_index_view(self):
        assert os.listdir(self.mount_path) == ['current', 'history']
