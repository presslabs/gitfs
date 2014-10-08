# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from datetime import datetime

from pygit2 import Repository as _Repository
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

        self.repo = Repository(_Repository(self.repo_path))
        self.repo.commits.update()

    def assert_new_commit(self, step=1):
        total_commits = BaseTest.COMMITS_DONE + step
        commits_len = len(self.commits)
        assert commits_len == total_commits
        BaseTest.COMMITS_DONE += step

    def assert_commit_message(self, message):
        self.repo.commits.update()
        commit = self.last_commit
        assert commit.message == message

    def assert_blob(self, blob, path):
        assert self.repo.get_blob_data(self.last_commit.tree, path) == blob

    @property
    def last_commit(self):
        self.repo.commits.update()
        last_commit = str(self.commits[-1])
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        return commit

    @property
    def commits(self):
        self.repo.commits.update()
        date = self.repo.get_commit_dates()
        return self.repo.get_commits_by_date(date[0])
