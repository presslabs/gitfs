import os

from tests.integrations.base import BaseTest


class TestHistoryCommitView(BaseTest):
    def test_listdirs(self):
        directory = os.listdir("%s/history/" % self.mount_path)
        assert directory == self.repo.get_commit_dates()
