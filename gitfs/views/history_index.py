
from datetime import datetime
from errno import ENOENT
from stat import S_IFDIR
from pygit2 import GIT_SORT_TIME

from .view import View
from gitfs import  FuseMethodNotImplemented, FuseOSError
from log import log


class HistoryIndexView(View):

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

    def _get_commit_dates(self):
        """
        Walk through all commits from current repo in order to compose the
        _history_ directory.
        """
        commit_dates = set()
        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
            commit_date = datetime.fromtimestamp(commit.commit_time).date()
            commit_dates.add(commit_date.strftime('%Y-%m-%d'))

        return list(commit_dates)

    def readdir(self, path, fh):
        commit_dates = self._get_commit_dates()

        dir_entries = ['.', '..'] + commit_dates
        for entry in dir_entries:
            yield entry
