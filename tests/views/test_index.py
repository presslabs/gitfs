# Copyright 2014 PressLabs SRL
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


from stat import S_IFDIR

import pytest

from fuse import FuseOSError

from gitfs.views.index import IndexView


class TestIndexView(object):
    def test_getattr_with_non_root_path(self):
        view = IndexView()

        with pytest.raises(FuseOSError):
            view.getattr("/path")

    def test_getattr_with_correct_path(self):
        view = IndexView(**{
            'uid': 1,
            'gid': 1,
            'mount_time': "now"
        })
        result = view.getattr("/", 1)

        asserted_result = {
            'st_mode': S_IFDIR | 0o555,
            'st_nlink': 2,
            'st_uid': 1,
            'st_gid': 1,
            'st_ctime': "now",
            'st_mtime': "now",
        }
        assert result == asserted_result

    def test_readdir(self):
        view = IndexView()
        assert view.readdir("path", 1) == ['.', '..', 'current', 'history']
