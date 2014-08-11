import os


class BaseTest(object):
    def setup(self):
        self.mount_path = "%s/" % os.environ["MOUNT_PATH"]
        self.repo_path = "%s/" % os.environ["REPO_PATH"]
