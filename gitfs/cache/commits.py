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


from datetime import datetime
from bisect import insort_left

from pygit2 import GIT_SORT_TIME


class CommitCache(object):
    def __init__(self, repo):
        self.repo = repo
        self.__commits = {}

    def update(self):
        new_commits = {}
        head = self.repo.lookup_reference('HEAD').resolve().target

        for commit in self.repo.walk(head, GIT_SORT_TIME):
            commit_time = datetime.fromtimestamp(commit.commit_time)

            date = commit_time.date().strftime('%Y-%m-%d')
            time = commit_time.time().strftime('%H-%M-%S')

            if date not in new_commits:
                new_commits[date] = []

            insort_left(new_commits[date], Commit(commit.commit_time, time,
                                                  commit.hex[:10]))

        self.__commits = new_commits

    def __getitem__(self, item):
        return self.__commits[item]

    def __setitem__(self, item, value):
        self.__commits[item] = value

    def __delitem__(self, item):
        del self.__commits[item]

    def keys(self):
        return self.__commits.keys()

    def __iter__(self):
        return iter(self.__commits)


class Commit(object):
    __slots__ = ['hex', 'time', 'timestamp']

    def __init__(self, timestamp, time, hex):
        self.hex = hex
        self.time = time
        self.timestamp = timestamp

    def __cmp__(self, commit):
        return self.timestamp > commit.timestamp

    def __repr__(self):
        return "%s-%s" % (self.time, self.hex[:10])
