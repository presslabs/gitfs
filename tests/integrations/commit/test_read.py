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

from six import iteritems

from tests.integrations.base import BaseTest


class TestReadCommitView(BaseTest):
    def test_listdirs(self):
        commits = self.get_commits_by_date()
        files = os.listdir("{}/history/{}/{}".format(
            self.mount_path, self.today, commits[-1]))

        real_files = os.listdir(self.repo_path)
        real_files.remove(".git")
        assert set(files) == set(real_files)

    def test_stats(self):
        commit = self.get_commits_by_date()[0]
        directory = "{}/history/{}/{}".format(self.mount_path, self.today, commit)
        filename = "{}/testing".format(directory)

        stats = os.stat(filename)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 0o100444,
        }

        for name, value in iteritems(attrs):
            assert getattr(stats, name) == value

        st_time = "{} {}".format(self.today, "-".join(commit.split("-")[:-1]))

        format = "%Y-%m-%d %H-%M-%S"
        ctime = datetime.fromtimestamp(stats.st_ctime).strftime(format)
        mtime = datetime.fromtimestamp(stats.st_ctime).strftime(format)

        assert ctime == st_time
        assert mtime == st_time
