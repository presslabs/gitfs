import os
from errno import EROFS, EACCES

from fuse import FuseOSError

from gitfs import FuseMethodNotImplemented

from .view import View


class ReadOnlyView(View):
    def getxattr(self, path, fh):
        raise FuseMethodNotImplemented

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
        if amode & (os.R_OK | os.F_OK):
            raise FuseOSError(EACCES)
        return 0

    def mkdir(self, path, mode):
        raise FuseOSError(EROFS)

    def utimens(self, path, times=None):
        raise FuseOSError(EROFS)

    def chown(self, path, uid, gid):
        raise FuseOSError(EROFS)

    def chmod(self, path, mode):
        raise FuseOSError(EROFS)
