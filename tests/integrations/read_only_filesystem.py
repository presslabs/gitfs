import pytest

from tests.integrations.base import BaseTest


class ReadOnlyFSTest(BaseTest):
    path = ""

    def test_write_to_new_file(self):
        filename = "%s/new_file" % self.path
        content = "Read only filesystem"

        with pytest.raises(IOError) as err:
            with open(filename, "w") as f:
                    f.write(content)

        assert err.value.errno == 30
        assert "Read-only file system" in str(err.value)
