import os

from tests.integrations.base import BaseTest


class TestReadCurrentView(BaseTest):
    def test_listdirs(self):
        dirs = set(os.listdir("%s/current" % self.mount_path))
        assert dirs == set(['testing', 'me'])

    def test_read_from_a_file(self):
        with open("%s/current/testing" % self.mount_path) as f:
            assert f.read() == "just testing around here\n"

    def test_get_correct_stats(self):
        filename = "%s/current/testing" % self.mount_path
        stats = os.stat(filename)

        filename = "%s/testing_repo/testing" % self.repo_path
        real_stats = os.stat(filename)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 0100644,
            'st_ctime': real_stats.st_ctime,
            'st_mtime': real_stats.st_mtime,
            'st_atime': real_stats.st_atime,
        }

        for name, value in attrs.iteritems():
            assert getattr(stats, name) == value
