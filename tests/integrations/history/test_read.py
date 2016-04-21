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


class TestHistoryView(BaseTest):
    def test_listdirs(self):
        directory = os.listdir("{}/history/".format(self.mount_path))
        assert directory == self.get_commit_dates()

    def test_listdirs_with_commits(self):
        commits = self.get_commits_by_date(self.today)[::-1]
        directory = os.listdir("{}/history/{}".format(self.mount_path, self.today))
        assert directory == commits

    def test_stats(self):
        directory = "{}/history/{}".format(self.mount_path, self.today)
        stats = os.stat(directory)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 0o40555,
        }

        for name, value in iteritems(attrs):
            assert getattr(stats, name) == value

        ctime = self._get_commit_time(0)
        mtime = self._get_commit_time(-1)

        assert ctime == self._from_timestamp(stats.st_ctime)
        assert mtime == self._from_timestamp(stats.st_mtime)

    def test_stats_with_commits(self):
        commit = self.get_commits_by_date(self.today)[0]
        directory = "{}/history/{}/{}".format(self.mount_path, self.today, commit)
        stats = os.stat(directory)

        attrs = {
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
            'st_mode': 0o40555,
        }
        for name, value in iteritems(attrs):
            assert getattr(stats, name) == value

        st_time = "{} {}".format(self.today, "-".join(commit.split("-")[:-1]))

        assert st_time == self._from_timestamp(stats.st_ctime)
        assert st_time == self._from_timestamp(stats.st_mtime)

    def _from_timestamp(self, timestamp, format="%Y-%m-%d %H-%M-%S",
                        utc=False):
        if utc:
            return datetime.utcfromtimestamp(timestamp).strftime(format)
        else:
            return datetime.fromtimestamp(timestamp).strftime(format)

    def _get_commit_time(self, index):
        commits = sorted(self.get_commits_by_date(self.today))
        return "{} {}".format(self.today, "-".join(commits[index].split("-")[:-1]))
