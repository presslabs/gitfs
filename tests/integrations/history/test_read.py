import os
from datetime import datetime

from gitfs.utils import strptime
from tests.integrations.base import BaseTest


class TestHistoryView(BaseTest):
    def test_listdirs(self):
        directory = os.listdir("%s/history/" % self.mount_path)
        assert directory == self.repo.get_commit_dates()

    def test_listdirs_with_commits(self):
        commits = self.repo.get_commits_by_date(self.today)
        directory = os.listdir("%s/history/%s" % (self.mount_path, self.today))
        assert directory == commits

    def test_stats(self):
        directory = "%s/history/%s" % (self.mount_path, self.today)
        stats = os.stat(directory)

        ctime = self._get_commit_time(0)
        mtime = self._get_commit_time(-1)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 040555,
        }

        print oct(stats.st_mode)
        for name, value in attrs.iteritems():
            assert getattr(stats, name) == value

        assert int(stats.st_ctime / 100) == int(ctime / 100)
        assert int(stats.st_mtime / 100) == int(mtime / 100)

    def _get_commit_time(self, index):
        commits = sorted(self.repo.get_commits_by_date(self.today))
        date_repr = "%s %s" % (self.today, commits[index].split("-")[0])
        date = strptime(date_repr, "%Y-%m-%d %H:%M:%S", True)
        return (date - datetime(1970, 1, 1)).total_seconds()

    def test_stats_with_commits(self):
        pass
