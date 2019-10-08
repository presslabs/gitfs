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


from fuse import FuseOSError
from mock import MagicMock, patch
import pytest
from gitfs.cache import CachedIgnore
from gitfs.utils.decorators.not_in import not_in


class TestNotIn(object):
    def test_decorator(self):
        mocked_function = MagicMock()
        mocked_function.__name__ = "function"
        mocked_object = MagicMock()
        mocked_object.ignore = CachedIgnore()
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]

        with patch.multiple("gitfs.utils.decorators.not_in", inspect=mocked_inspect):
            not_in("ignore", check=["file"])(mocked_function)(mocked_object, "file")

        mocked_function.assert_called_once_with(mocked_object, "file")

    def test_in_cache(self):
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]
        mocked_gitignore = MagicMock()
        mocked_gitignore.get.return_value = True
        mocked_look_at = MagicMock()
        mocked_look_at.cache = mocked_gitignore

        with patch.multiple("gitfs.utils.decorators.not_in", inspect=mocked_inspect):
            with pytest.raises(FuseOSError):
                not_in(mocked_look_at, check=["file"]).check_args(None, "file")

    def test_has_key(self):
        mocked_inspect = MagicMock()
        mocked_inspect.getargspec.return_value = [["file"]]
        mocked_gitignore = MagicMock()
        mocked_gitignore.get.return_value = False
        mocked_look_at = MagicMock()
        mocked_look_at.cache = mocked_gitignore
        mocked_look_at.check_key.return_value = True

        with patch.multiple("gitfs.utils.decorators.not_in", inspect=mocked_inspect):
            with pytest.raises(FuseOSError):
                not_in(mocked_look_at, check=["file"]).check_args(None, "file")
