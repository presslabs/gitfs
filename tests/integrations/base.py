import os
from datetime import datetime

from gitfs.utils.repository import Repository


class BaseTest(object):
    COMMITS_DONE = 1

    @property
    def today(self):
        now = datetime.now()
        return "%s-%s-%s" % (now.year, now.month, now.day)

    def setup(self):
        self.mount_path = "%s/" % os.environ["MOUNT_PATH"]
        self.repo_path = "%s/" % os.environ["REPO_PATH"]

        self.repo = Repository("%s/testing_repo/" % self.repo_path)

    def assert_new_commit(self):
        total_commits = BaseTest.COMMITS_DONE + 1
        commits_len = len(self.commits)
        assert commits_len == total_commits
        BaseTest.COMMITS_DONE = BaseTest.COMMITS_DONE + 1

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
