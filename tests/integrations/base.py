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


from contextlib import contextmanager
from datetime import datetime
import collections
import os
import subprocess
import time

import pytest


class Sh:
    def __init__(self, cwd=None):
        self.command = ""
        self.cwd = cwd

    def __getattr__(self, item):
        self.command += item + " "

        return self

    def __call__(self, *args, **kwargs):
        command = self.command + " ".join(args)
        self.command = ""

        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                cwd=self.cwd).stdout.read()


class pull:
    def __init__(self, sh):
        self.sh = sh

    def __enter__(self):
        self.sh.git.pull("origin", "master")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class BaseTest(object):
    def setup(self):
        self.mount_path = "%s" % os.environ["MOUNT_PATH"]

        self.repo_name = os.environ["REPO_NAME"]
        self.repo_path = os.environ["REPO_PATH"]

        self.current_path = "%s/current" % self.mount_path

        self.remote_repo_path = os.environ["REMOTE"]
        self.sh = Sh(self.remote_repo_path)

        self.last_commit_hash = self.commit_hash()

    @property
    def today(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    def commit_hash(self, index=0):
        return self.sh.git.log("--pretty=%H").splitlines()[index]

    def commit_message(self, index=0):
        return self.sh.git.log("--pretty=%B").splitlines()[index]

    def get_commits_by_date(self, date=None):
        if date is None:
            date = self.today

        lines = self.sh.git.log("--before", '"%s 23:59:59"' % date,
                                "--after", '"%s 00:00:00"' % date,
                                '--pretty="%ai %H"').splitlines()

        lines = map(lambda line: line.split(), lines)

        return map(lambda tokens: "%s-%s" % (tokens[1].replace(":", "-"),
                                             tokens[3][:10]), lines)

    def get_commit_dates(self):
        return list(set(self.sh.git.log("--pretty=%ad", "--date=short").
                        splitlines()))

    def assert_commit_message(self, message):
        assert message == self.commit_message()

    def assert_new_commit(self, steps=1):
        current_index = 0

        while self.commit_hash(current_index) != self.last_commit_hash:
            current_index += 1

        self.last_commit_hash = self.commit_hash(0)

        assert current_index == steps

    def assert_file_content(self, file_path, content):
        with open(self.repo_path + "/" + file_path) as f:
            assert f.read() == content


class GitFSLog(object):
    def __init__(self, file_descriptor):
        self._partial_line = None
        self.line_buffer = collections.deque()
        self.file_descriptor = file_descriptor

    def get_line(self):
        if not self.line_buffer:
            self._read_data()
        if self.line_buffer:
            return self.line_buffer.popleft()

    def _read_data(self):
        data = os.read(self.file_descriptor, 2048).splitlines(True)
        if not data:
            return
        if self._partial_line:
            data[0] = self._partial_line + data[0]
        if not data[-1].endswith("\n"):
            self._partial_line = data[-1]
            data = data[:-1]  # discard the partial line
        else:
            self._partial_line = None
        self.line_buffer.extend(data)

    def clear(self):
        while os.read(self.file_descriptor, 2048):
            pass
        self._partial_line = None
        self.line_buffer = collections.deque()

    def __call__(self, expected, **kwargs):
        @contextmanager
        def log_context(gitfs_log):
            gitfs_log.clear()
            yield
            if isinstance(expected, basestring):
                gitfs_log.expect(expected, **kwargs)
            else:
                gitfs_log.expect_multiple(expected, **kwargs)
        return log_context(self)

    def expect(self, expected, timeout=10, pollfreq=0.1):
        elapsed = 0
        while elapsed < timeout:
            line = self.get_line()
            # if we didn'g get anything re-try to read the line
            while line is None and elapsed < timeout:
                time.sleep(pollfreq)
                elapsed += pollfreq
                line = self.get_line()
            if line is not None and expected in line:
                return line
        raise AssertionError("expected '{}' not found in stream".format(expected))

    def expect_multiple(self, expected, *args, **kwargs):
        for exp in expected:
            self.expect(exp, *args, **kwargs)


@pytest.fixture(scope='session')
def gitfs_log():
    return GitFSLog(os.open("log.txt", os.O_NONBLOCK))
