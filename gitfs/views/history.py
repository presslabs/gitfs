import os
from datetime import datetime
from stat import S_IFDIR
from errno import ENOENT, EROFS

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

        if path not in self._get_commit_dates() and path != '/':
            raise FuseOSError(ENOENT)

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

    def open(self, path, fh):
        return 0

    def create(self, path, fh):
        raise FuseOSError(EROFS)

    def write(self, path, fh):
        raise FuseOSError(EROFS)

    def access(self, path, amode):
        if getattr(self, 'date', None):
            log.info('PATH: %s', path)
            if path == '/':
                available_dates = self._get_commit_dates()
                if self.date not in available_dates:
                    raise FuseOSError(ENOENT)
            else:
                commits = self._get_commits_by_date(self.date)
                dirname = os.path.split(path)[1]
                if dirname not in commits:
                    raise FuseOSError(ENOENT)
        else:
            if path != '/':
                raise FuseOSError(ENOENT)
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

    def _get_commits_by_date(self, date):
        """
        Retrieves all the commits from a particular date.

        :param date: date with the format: yyyy-mm-dd
        :type date: str
        :returns: a list containg the commits for that day. Each list item
            will have the format: hh:mm:ss-<short_sha1>, where short_sha1 is
            the short sha1 of the commit.
        :rtype: list
        """

        date = strptime(date, '%Y-%m-%d')
        commits = []
        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
            commit_time = datetime.fromtimestamp(commit.commit_time)
            if commit_time.date() == date:
                time = commit_time.time().strftime('%H:%M:%S')
                commits.append("%s-%s" % (time, commit.hex[:10]))
        return commits

    def readdir(self, path, fh):
        if getattr(self, 'date', None):
            additional_entries = self._get_commits_by_date(self.date)
        else:
            additional_entries = self._get_commit_dates()

        dir_entries = ['.', '..'] + additional_entries
        for entry in dir_entries:
            yield entry
