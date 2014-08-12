import os

from tests.integrations.base import BaseTest


class TestWriteCurrentView(BaseTest):
    def setup(self):
        super(TestWriteCurrentView, self).setup()
        self.current = "%s/current/" % self.mount_path

    def test_write_a_file(self):
        content = "Just a small file"
        filename = "%s/new_file" % self.current

        with open(filename, "w") as f:
            f.write(content)

        # check if the write was done correctly
        with open(filename) as f:
            assert f.read() == content

        # check if a commit was made
        date = self.repo.get_commit_dates()
        commits = self.repo.get_commits_by_date(date[0])
        assert len(commits) == 2

        # check if the commit contains the right blob
        last_commit = commits[0]
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        assert self.repo.get_blob_data(commit.tree, "new_file") == content

        # check for the right commit message
        assert commit.message == "Update /new_file"

    def test_create_a_directory(self):
        directory = "%s/new_directory" % self.current

        os.makedirs(directory)

        # check if directory exists or not
        directory_path = "%s/testing_repo/new_directory" % self.repo_path
        assert os.path.exists(directory_path)

        # check for .keep file
        keep_path = "%s/testing_repo/new_directory/.keep" % self.repo_path
        assert os.path.exists(keep_path)

        # check if a commit was made
        date = self.repo.get_commit_dates()
        commits = self.repo.get_commits_by_date(date[0])
        assert len(commits) == 3

        # check for the right commit message
        last_commit = commits[0]
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        assert commit.message == "Created new_directory/.keep"

    def test_chmod(self):
        filename = "%s/testing" % self.current
        os.chmod(filename, 0766)

        # check if the right mode was set
        stats = os.stat(filename)
        assert stats.st_mode == 0100766

        # check if a commit was made
        date = self.repo.get_commit_dates()
        commits = self.repo.get_commits_by_date(date[0])
        assert len(commits) == 4

        # check for the right commit message
        last_commit = commits[0]
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        assert commit.message == "Chmod to 0766 on /testing"

    def test_rename(self):
        old_filename = "%s/testing" % self.current
        new_filename = "%s/new_testing" % self.current

        os.rename(old_filename, new_filename)

        # check for new file
        assert os.path.exists(new_filename)

        # check if a commit was made
        date = self.repo.get_commit_dates()
        commits = self.repo.get_commits_by_date(date[0])
        assert len(commits) == 5

        # check for the right commit message
        last_commit = commits[0]
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        assert commit.message == "Rename /testing to /new_testing"

    def test_fsync(self):
        filename = "%s/me" % self.current
        content = "test fsync"

        with open(filename, "w") as f:
            f.write(content)
            os.fsync(f.fileno())

        # check if a commit was made
        date = self.repo.get_commit_dates()
        commits = self.repo.get_commits_by_date(date[0])
        assert len(commits) == 6

        # check for the right commit message
        last_commit = commits[0]
        commit = self.repo.revparse_single(last_commit.split('-')[1])
        assert commit.message == "Fsync /me"
