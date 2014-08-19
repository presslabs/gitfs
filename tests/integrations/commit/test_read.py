import os

from tests.integrations.base import BaseTest


class TestReadCommitView(BaseTest):

    def test_listdirs(self):
        commits = self.repo.get_commits_by_date(self.today)
        files = os.listdir("%s/history/%s/%s" % (self.mount_path, self.today, commits[-1]))

        real_files = os.listdir("%s/testing_repo/" % self.repo_path)
        real_files.remove(".git")
        assert set(files) == set(real_files)
