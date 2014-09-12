import time
import os
from stat import S_IFDIR
from errno import ENOENT

from fuse import FuseOSError

from gitfs.log import log
from gitfs.cache import lru_cache

from .read_only import ReadOnlyView


class HistoryView(ReadOnlyView):

    @lru_cache(4000)
    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        if path not in self.repo.get_commit_dates() and path != '/':
            raise FuseOSError(ENOENT)

        attrs = super(HistoryView, self).getattr(path, fh)
        attrs.update({
            'st_mode': S_IFDIR | 0555,
            'st_nlink': 2,
            'st_ctime': self._get_first_commit_time(),
            'st_mtime': self._get_last_commit_time(),
        })

        return attrs

    def access(self, path, mode):
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

    def _get_commit_time(self, index):
        date = getattr(self, 'date', None)

        if date and date in self.repo.commits:
            return self.repo.commits[date][index].timestamp

        return int(time.time())

    def _get_last_commit_time(self):
        return self._get_commit_time(-1)

    def _get_first_commit_time(self):
        return self._get_commit_time(0)
