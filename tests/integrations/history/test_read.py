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

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 040555,
        }

        for name, value in attrs.iteritems():
            assert getattr(stats, name) == value

        ctime = self._get_commit_time(0)

        assert ctime == self._from_timestamp(stats.st_ctime, utc=True)
        assert ctime == self._from_timestamp(stats.st_mtime, utc=True)

    def _from_timestamp(self, timestamp, format="%Y-%m-%d %H:%M:%S",
                        utc=False):
        if utc:
            return datetime.utcfromtimestamp(timestamp).strftime(format)
        else:
            return datetime.fromtimestamp(timestamp).strftime(format)

    def _get_commit_time(self, index):
        commits = sorted(self.repo.get_commits_by_date(self.today))
        print commits
        return "%s %s" % (self.today, commits[index].split("-")[0])

    def test_stats_with_commits(self):
        commit = self.repo.get_commits_by_date(self.today)[0]
        directory = "%s/history/%s/%s" % (self.mount_path, self.today, commit)
        stats = os.stat(directory)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 040555,
        }
        for name, value in attrs.iteritems():
            assert getattr(stats, name) == value

        st_time = "%s %s" % (self.today, commit.split("-")[0])

        assert st_time == self._from_timestamp(stats.st_ctime)
        assert st_time == self._from_timestamp(stats.st_mtime)
