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
