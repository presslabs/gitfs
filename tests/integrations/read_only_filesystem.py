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


import pytest
import errno

from tests.integrations.base import BaseTest


class ReadOnlyFSTest(BaseTest):
    path = ""

    def test_write_to_new_file(self):
        filename = "{}/new_file".format(self.path)
        content = "Read only filesystem"

        with pytest.raises(IOError) as err:
            with open(filename, "w") as f:
                f.write(content)

        assert err.value.errno == errno.EROFS
        assert "Read-only file system" in str(err.value)
