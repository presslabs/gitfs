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


from mock import MagicMock, patch
from gitfs.cache import CachedIgnore


class TestCachedIgnore(object):
    def test_init(self):
        mocked_os = MagicMock()
        mocked_os.path.exists.return_value = True
        mocked_re = MagicMock()
        mocked_re.findall.return_value = [[None, None, "found"]]

        with patch("gitfs.cache.gitignore.open", create=True) as mocked_open:
            mocked_file = mocked_open.return_value.__enter__.return_value
            mocked_file.read.return_value = "file"

            with patch.multiple("gitfs.cache.gitignore", os=mocked_os, re=mocked_re):
                gitignore = CachedIgnore("some_file", "some_file")

                assert gitignore.items == [
                    ".git",
                    ".git/*",
                    "/.git/*",
                    "*.keep",
                    "*.gitmodules",
                    "/found/*",
                    "/found",
                    "found",
                ]

    def test_update(self):
        gitignore = CachedIgnore()
        gitignore.cache = {"some_key": "some_value"}

        gitignore.update()

        assert gitignore.cache == {}

    def test_contains(self):
        gitignore = CachedIgnore()

        assert ".git" in gitignore
        assert "file" not in gitignore
