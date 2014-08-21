from tests.integrations import ReadOnlyFSTest


class TestWriteIndexView(ReadOnlyFSTest):
    def setup(self):
        super(TestWriteIndexView, self).setup()
        self.path = self.mount_path
