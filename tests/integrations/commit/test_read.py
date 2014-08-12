import os
from datetime import datetime

from tests.integrations.base import BaseTest


class TestReadCommitView(BaseTest):
    def test_listdirs(self):
        now = datetime.now()
        today = "%s-%s-%s" % (now.year, now.month, now.day)

        commits = self.repo.get_commits_by_date(today)
        directory = os.listdir("%s/history/%s" % (self.mount_path, today))
        assert directory == commits
