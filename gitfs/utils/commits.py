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


class CommitsList(object):
    def __init__(self, commits=None, hashes=None):
        self.commits = commits or []
        self.hashes = hashes or []

    def __contains__(self, commit):
        return commit.hex in self.hashes

    def index(self, commit):
        return self.hashes.index(commit.hex)

    def __getitem__(self, val):
        commits = self.commits[val]
        hashes = self.hashes[val]
        return CommitsList(commits, hashes)

    def __iter__(self):
        return self.commits.__iter__()

    def append(self, commit):
        self.commits.append(commit)
        self.hashes.append(commit.hex)

    def __repr__(self):
        return self.commits.__repr__()

    def __len__(self):
        return len(self.commits)
