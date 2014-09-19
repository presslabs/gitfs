from tests.integrations import ReadOnlyFSTest


class TestWriteCommitView(ReadOnlyFSTest):
    def setup(self):
        super(TestWriteCommitView, self).setup()
        date = self.get_commit_dates()
        self.path = "%s/history/%s/%s" % (self.mount_path, date[0],
                                          self.get_commits_by_date()[0])
