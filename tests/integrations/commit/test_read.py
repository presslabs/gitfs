import os
from datetime import datetime

from tests.integrations.base import BaseTest


class TestReadCommitView(BaseTest):
    def test_listdirs(self):
        commits = self.get_commits_by_date()
        files = os.listdir("%s/history/%s/%s" % (self.mount_path, self.today,
                           commits[-1]))

        real_files = os.listdir(self.repo_path)
        real_files.remove(".git")
        assert set(files) == set(real_files)

    def test_stats(self):
        commit = self.get_commits_by_date()[0]
        directory = "%s/history/%s/%s" % (self.mount_path, self.today, commit)
        filename = "%s/testing" % directory

        stats = os.stat(filename)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 0100444,
        }

        for name, value in attrs.iteritems():
            assert getattr(stats, name) == value

        st_time = "%s %s" % (self.today, commit.split("-")[0])

        format = "%Y-%m-%d %H:%M:%S"
        ctime = datetime.fromtimestamp(stats.st_ctime).strftime(format)
        mtime = datetime.fromtimestamp(stats.st_ctime).strftime(format)

        assert ctime == st_time
        assert mtime == st_time
