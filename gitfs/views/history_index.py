
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

    def _get_commit_history(self):
        """
        Walk through all commits from current repo in order to compose the
        _history_ directory.
        """
        paths = {}

        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
            commit_time = datetime.fromtimestamp(commit.commit_time)

            day = commit_time.date().strftime('%Y-%m-%d')
            time = commit_time.time().strftime('%H-%m-%S')

            paths[day] = "%s-%s" % (time, commit.hex[:7])
            #paths[day] = "%s-%s" % (time, commit.hex)

        return paths

    def readdir(self, path, fh):
        commit_hist = self._get_commit_history()

        dir_entries = ['.', '..'] + commit_hist.keys()
        for entry in dir_entries:
            yield entry
