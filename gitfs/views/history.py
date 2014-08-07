import os
from datetime import datetime
from stat import S_IFDIR
from errno import ENOENT

from pygit2 import GIT_SORT_TIME
from fuse import FuseOSError

from gitfs.utils import strptime
from gitfs.log import log

from .view import View


class HistoryView(View):

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        attrs = super(HistoryView, self).getattr(path, fh)
        attrs.update({
            'st_mode': S_IFDIR | 0775,
            'st_nlink': 2
        })

        return attrs

    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        if getattr(self, 'date', None):
            log.info('PATH: %s', path)
            if path == '/':
                available_dates = self.repo.get_commit_dates()
                if self.date not in available_dates:
                    raise FuseOSError(ENOENT)
            else:
                commits = self.repo.get_commits_by_date(self.date)
                dirname = os.path.split(path)[1]
                if dirname not in commits:
                    raise FuseOSError(ENOENT)
        else:
            if path != '/':
                raise FuseOSError(ENOENT)
        return 0

    def readdir(self, path, fh):
        if getattr(self, 'date', None):
            additional_entries = self.repo.get_commits_by_date(self.date)
        else:
            additional_entries = self.repo.get_commit_dates()

        dir_entries = ['.', '..'] + additional_entries
        for entry in dir_entries:
            yield entry
