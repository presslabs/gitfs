import os
from stat import S_IFDIR
from pygit2 import GIT_FILEMODE_TREE

from log import log
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

        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)


    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        log.info('%s %s', path, amode)
        return 0

    def _get_commit_subtree(self, tree, subtree_name):
        for e in tree:
            if e.filemode == GIT_FILEMODE_TREE:
                if e.name == subtree_name:
                    return self.repo[e.id]
                else:
                    return self._get_commit_subtree(self.repo[e.id],
                                                    subtree_name)

    def readdir(self, path, fh):
        dir_entries = ['.', '..']
        commit = self.repo.revparse_single(self.commit_sha1)
        if getattr(self, 'relative_path'):
            tree_name = os.path.split(self.relative_path)[1]
            subtree = self._get_commit_subtree(commit.tree, tree_name)
            [dir_entries.append(entry.name) for entry in subtree]
        else:
            [dir_entries.append(entry.name) for entry in commit.tree]
        return dir_entries
