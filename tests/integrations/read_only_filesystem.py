import pytest

from .base import BaseTest


class ReadOnlyFSTest(BaseTest):
    path = ""

    @pytest.mark.xfail(raises=IOError)
    def test_write_to_new_file(self):
        filename = "%s/new_file" % self.path
        content = "Read only filesystem"

        with open(filename, "w") as f:
                f.write(content)
