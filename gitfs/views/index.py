import os
from errno import ENOENT
from stat import S_IFDIR
from gitfs import  FuseMethodNotImplemented, FuseOSError

from .view import View
from log import log


class IndexView(View):

    def statfs(self, path):
        return {}

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        if path != '/':
            raise FuseOSError(ENOENT)
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)


    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        log.info('%s %s', path, amode)
        return 0

    def readdir(self, path, fh):
        #dirents = [
            #('.', {'st_ino': 1, 'st_mode': S_IFDIR}),
            #('..', {'st_ino': 2, 'st_mode': S_IFDIR}),
            #('current', {'st_ino': 3, 'st_mode': S_IFDIR}),
            #('history', {'st_ino': 4, 'st_mode': S_IFDIR})]
        #return dirents
        return ['.', '..', 'current', 'history']

