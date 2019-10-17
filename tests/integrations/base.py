# Copyright 2014-2016 Presslabs SRL
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
from six import string_types


class Sh(object):
    def __init__(self, cwd=None):
        self.command = ""
        self.cwd = cwd

    def __getattr__(self, item):
        self.command += item + " "

        return self

    def __call__(self, *args, **kwargs):
        command = self.command + " ".join(args)
        self.command = ""

        return (
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, cwd=self.cwd)
            .stdout.read()
            .decode()
        )


class pull(object):
    def __init__(self, sh):
        self.sh = sh

    def __enter__(self):
        self.sh.git.pull("origin", "master")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class BaseTest(object):
    def setup(self):
        self.mount_path = "{}".format(os.environ["MOUNT_PATH"])

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

        lines = self.sh.git.log(
            "--before",
            '"%s 23:59:59"' % date,
            "--after",
            '"%s 00:00:00"' % date,
            '--pretty="%ai %H"',
        ).splitlines()

        lines = map(lambda line: line.split(), lines)

        return list(
            map(
                lambda tokens: "%s-%s" % (tokens[1].replace(":", "-"), tokens[3][:10]),
                lines,
            )
        )

    def get_commit_dates(self):
        return list(set(self.sh.git.log("--pretty=%ad", "--date=short").splitlines()))

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

    def _read_data(self):
        # file should be opened in non-blocking mode, so this will
        # return None if it can't read any data
        data = os.read(self.file_descriptor, 2048).decode().splitlines(True)
        if not data:
            return False
        if self._partial_line:
            data[0] = self._partial_line + data[0]
        if not data[-1].endswith("\n"):
            self._partial_line = data[-1]
            data = data[:-1]  # discard the partial line
        else:
            self._partial_line = None
        self.line_buffer.extend(data)
        return True

    def clear(self):
        """Discards any logs produced so far."""
        # seek to the end of the file, since we want to discard old messages
        os.lseek(self.file_descriptor, 0, os.SEEK_END)
        self._partial_line = None
        self.line_buffer = collections.deque()

    def __call__(self, expected, **kwargs):
        """Returns a context manager so you can wrap operations with expected
        log output.

        Example usage:
        with gitfs_log("Expected log output"):
            do_operation_that_produces_expected_log_output()
        """

        @contextmanager
        def log_context(gitfs_log):
            gitfs_log.clear()
            yield
            if isinstance(expected, string_types):
                gitfs_log.expect(expected, **kwargs)
            else:
                gitfs_log.expect_multiple(expected, **kwargs)

        return log_context(self)

    def _get_line(self, timeout, pollfreq=0.01):
        """Blocks until it can return a line. Returns None if it timedout."""
        if self.line_buffer:
            # got buffered lines, consume from these first
            return self.line_buffer.popleft()
        elapsed = 0
        while elapsed < timeout:
            if self._read_data():
                return self.line_buffer.popleft()
            time.sleep(pollfreq)
            elapsed += pollfreq
        return None

    def expect(self, expected, timeout=10):
        """Blocks untill `expected` is found in a line of the stream,
        or until timeout is reached.
        """
        started = time.time()
        elapsed = 0
        while elapsed < timeout:
            line = self._get_line(timeout=(timeout - elapsed))
            if line is None:
                break  # timed out waiting for line
            elif expected in line:
                return
            elapsed = time.time() - started
        raise AssertionError(
            "Timed out waiting for '{}' in the stream".format(expected)
        )

    def expect_multiple(self, expected, *args, **kwargs):
        """Blocks untill all `expected` strings are found in the stream, in the
        order they were passed.
        """
        for exp in expected:
            self.expect(exp, *args, **kwargs)


@pytest.fixture(scope="session")
def gitfs_log():
    return GitFSLog(os.open("log.txt", os.O_NONBLOCK))
