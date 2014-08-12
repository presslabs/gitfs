import os

from gitfs.utils.repository import Repository


class BaseTest(object):
    def setup(self):
        self.mount_path = "%s/" % os.environ["MOUNT_PATH"]
        self.repo_path = "%s/" % os.environ["REPO_PATH"]

        self.repo = Repository("%s/" % self.repo_path)
