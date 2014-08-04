import os
from stat import S_IFDIR
from pygit2 import GIT_FILEMODE_TREE

from log import log
from .view import View


class CommitView(View):

    def __init__(self, *args, **kwargs):
        super(CommitView, self).__init__(*args, **kwargs)
        print self.relative_path
        # self.dir_entries = self._get_dir_entries(self.relative_path)
        # print self.dir_entries

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        print path
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)

    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        log.info('%s %s', path, amode)
        return 0

    def _get_commit_subtree(self, tree, subtree_name):
        """
        Retrievs from the repo the Tree object with the name <subtree_name>.

        :param tree: a pygit2.Tree instance
        :param subtree_name: the name of the tree that is being searched for.
        :type subtree_name: str
        :returns: a pygit2.Tree instance representig the tree that is was
            searched for.
        """
        for node in tree:
            if node.filemode == GIT_FILEMODE_TREE:
                if node.name == subtree_name:
                    return self.repo[node.id]
                else:
                    return self._get_commit_subtree(self.repo[node.id],
                                                    subtree_name)

    def _get_dir_entries(self, name):
        dir_entries = []
        commit = self.repo.revparse_single(self.commit_sha1)
        dir_tree = commit.tree

        # If the relative_path is not empty, fetch the git tree corresponding
        # to the directory that we are in.
        tree_name = os.path.split(self.relative_path)[1]
        if tree_name:
            subtree = self._get_commit_subtree(commit.tree, tree_name)
            dir_tree = subtree

        [dir_entries.append(entry) for entry in dir_tree]

        return dir_entries

    def readdir(self, path, fh):
        dir_entries = ['.', '..']
        commit = self.repo.revparse_single(self.commit_sha1)
        dir_tree = commit.tree

        # If the relative_path is not empty, fetch the git tree corresponding
        # to the directory that we are in.
        tree_name = os.path.split(self.relative_path)[1]
        if tree_name:
            subtree = self._get_commit_subtree(commit.tree, tree_name)
            dir_tree = subtree

        [dir_entries.append(entry.name) for entry in dir_tree]
        # [dir_entries.append(entry.name) for entry in self.dir_entries]
        return dir_entries

    # def open(self, path, flags):
        # full_path = self._full_path(path)
        # return os.open(full_path, flags)

    # def read(self, path, length, offset, fh):
        # print path
        # os.lseek(fh, offset, os.SEEK_SET)
        # return os.read(fh, length)
