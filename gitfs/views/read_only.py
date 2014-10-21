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


import os
from errno import EROFS

from fuse import FuseOSError, ENOTSUP

from .view import View


class ReadOnlyView(View):
    def getxattr(self, path, name, *args):
        raise FuseOSError(ENOTSUP)

    def open(self, path, flags):
        write_flags = (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_TRUNC
                       | os.O_CREAT)

        if write_flags & flags:
            raise FuseOSError(EROFS)

        return 0

    def create(self, path, fh):
        raise FuseOSError(EROFS)

    def write(self, path, fh):
        raise FuseOSError(EROFS)

    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        return 0

    def flush(self, path, fh):
        return 0

    def release(self, path, fh):
        return 0

    def access(self, path, amode):
        if amode & os.W_OK:
            raise FuseOSError(EROFS)
        return 0

    def mkdir(self, path, mode):
        raise FuseOSError(EROFS)

    def utimens(self, path, times=None):
        raise FuseOSError(EROFS)

    def chown(self, path, uid, gid):
        raise FuseOSError(EROFS)

    def chmod(self, path, mode):
        raise FuseOSError(EROFS)
