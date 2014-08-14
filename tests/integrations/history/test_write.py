from tests.integrations import ReadOnlyFSTest


class TestWriteHistoryView(ReadOnlyFSTest):
    def setup(self):
        super(TestWriteHistoryView, self).setup()
        self.path = "%s/history" % self.mount_path
