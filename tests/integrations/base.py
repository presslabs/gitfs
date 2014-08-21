import os
from datetime import datetime

from gitfs.utils.repository import Repository


class BaseTest(object):
    COMMITS_DONE = 1

    @property
    def today(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    def setup(self):
        self.mount_path = "%s/" % os.environ["MOUNT_PATH"]
        self.repo_name = os.environ["REPO_NAME"]
        self.repo_path = "%s/%s" % (os.environ["REPO_PATH"], self.repo_name)

        self.current_path = "%s/current" % self.mount_path

        self.repo = Repository(self.repo_path)

    def assert_new_commit(self):
        total_commits = self.COMMITS_DONE
        commits_len = len(self.commits)
        assert commits_len == total_commits

    def assert_commit_message(self, message):
        commit = self.last_commit
        assert commit.message == message

    def assert_blob(self, blob, path):
        assert self.repo.get_blob_data(self.last_commit.tree, path) == blob

    @property
    def last_commit(self):
        last_commit = self.commits[0]
        return self.repo.revparse_single(last_commit.split('-')[1])

    @property
    def commits(self):
        date = self.repo.get_commit_dates()
        return self.repo.get_commits_by_date(date[0])
