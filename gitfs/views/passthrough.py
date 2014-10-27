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
from fuse import FuseOSError
from errno import EACCES

from .view import View

STATS = ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink',
         'st_size', 'st_uid')

FS_STATS = ('f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail',
            'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax')


class PassthroughView(View):

    def __init__(self, *args, **kwargs):
        super(PassthroughView, self).__init__(*args, **kwargs)
        self.repo = kwargs['repo']
        self.root = kwargs['repo_path']

    def access(self, path, mode):
        full_path = self.repo._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(EACCES)
        if path.endswith('/.git'):
            raise FuseOSError(EACCES)
        return 0

    def chmod(self, path, mode):
        full_path = self.repo._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self.repo._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self.repo._full_path(path)
        status = os.lstat(full_path)
        return dict((key, getattr(status, key)) for key in STATS)

    def readdir(self, path, fh):
        full_path = self.repo._full_path(path)

        dirents = ['.', '..']
        hidden_items = ['.git', '.keep']
        if os.path.isdir(full_path):
            for entry in os.listdir(full_path):
                if entry not in hidden_items:
                    dirents.append(entry)

        for directory in dirents:
            yield directory

    def readlink(self, path):
        pathname = os.readlink(self.repo._full_path(path))
        if pathname.startswith("/"):
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self.repo._full_path(path), mode, dev)

    def rmdir(self, path):
        return os.rmdir(self.repo._full_path(path))

    def mkdir(self, path, mode):
        return os.mkdir(self.repo._full_path(path), mode)

    def statfs(self, path):
        full_path = self.repo._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in FS_STATS)

    def unlink(self, path):
        return os.unlink(self.repo._full_path(path))

    def symlink(self, target, name):
        target = self.repo._full_path(target)
        name = self.repo._full_path(name)
        return os.symlink(target, name)

    def rename(self, old, new):
        old = self.repo._full_path(old)
        new = self.repo._full_path(new)
        return os.rename(old, new)

    def link(self, target, name):
        target = self.repo._full_path(target)
        name = self.repo._full_path(name)
        return os.link(target, name)

    def utimens(self, path, times=None):
        return os.utime(self.repo._full_path(path), times)

    def open(self, path, flags):
        full_path = self.repo._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self.repo._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self.repo._full_path(path)
        with open(full_path, 'r+') as input_file:
            input_file.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return os.fsync(fh)
