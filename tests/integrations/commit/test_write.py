from tests.integrations import ReadOnlyFSTest


class TestWriteCommitView(ReadOnlyFSTest):
    def setup(self):
        super(TestWriteCommitView, self).setup()
        date = self.repo.get_commit_dates()
        self.path = "%s/history/%s/%s" % (self.mount_path, date[0],
                                          self.commits[0])
