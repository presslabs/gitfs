
from datetime import datetime
from errno import ENOENT
from stat import S_IFDIR
from pygit2 import GIT_SORT_TIME

from .view import View
from gitfs import  FuseMethodNotImplemented, FuseOSError
from log import log


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

        date = datetime.strptime(date, '%Y-%m-%d').date()
        commits = []
        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
            commit_time = datetime.fromtimestamp(commit.commit_time)
            if  commit_time.date() == date:
                time = commit_time.time().strftime('%H:%M:%S')
                commits.append("%s-%s" % (time, commit.hex[:10]))

        return commits

    def readdir(self, path, fh):
        dir_entries = ['.', '..']
        if getattr(self, 'date', None):
            additional_entries = self._get_commits_by_date(self.date)
        else:
            additional_entries = self._get_commit_dates()

        dir_entries += additional_entries

        for entry in dir_entries:
            yield entry
