from errno import EROFS

from fuse import FuseOSError

from gitfs import FuseMethodNotImplemented

from .view import View


class ReadOnlyView(View):
    def getxattr(self, path, fh):
        raise FuseMethodNotImplemented

    def open(self, path, fh):
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
        return 0

    def mkdir(self, path, mode):
        raise FuseOSError(EROFS)
