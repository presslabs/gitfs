from datetime import datetime
import os
import subprocess


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


def pull(function):
    def call(*args, **kwargs):
        args[0].sh.git.pull("origin", "master")

        return function(*args, **kwargs)
    return call


class BaseTest(object):
    def setup(self):
        self.mount_path = "%s" % os.environ["MOUNT_PATH"]

        self.repo_name = os.environ["REPO_NAME"]
        self.repo_path = "%s/%s" % (os.environ["REPO_PATH"], self.repo_name)

        self.current_path = "%s/current" % self.mount_path

        self.sh = Sh(self.repo_path)

        self.last_commit_hash = self.commit_hash()

    @property
    def today(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    @pull
    def commit_hash(self, index=0):
        return self.sh.git.log("--pretty=%H").splitlines()[index]

    @pull
    def commit_message(self, index=0):
        return self.sh.git.log("--pretty=%B").splitlines()[index]

    @pull
    def get_commits_by_date(self, date=None):
        if date is None:
            date = self.today

        lines = self.sh.git.log("--before", '"%s 23:59:59"' % date,
                                "--after", '"%s 00:00:00"' % date,
                                '--pretty="%ai %H"').splitlines()

        lines = map(lambda line: line.split(), lines)

        return map(lambda tokens: "%s-%s" % (tokens[1], tokens[3][:10]), lines)

    @pull
    def get_commit_dates(self):
        return list(set(self.sh.git.log("--pretty=%ad", "--date=short").
                        splitlines()))

    @pull
    def assert_commit_message(self, message):
        assert message == self.commit_message()

    @pull
    def assert_new_commit(self, steps=1):
        current_index = 0

        while self.commit_hash(current_index) != self.last_commit_hash:
            current_index += 1

        self.last_commit_hash = self.commit_hash(0)

        assert current_index == steps

    @pull
    def assert_file_content(self, file_path, content):
        with open(self.repo_path + "/" + file_path) as f:
            assert f.read() == content