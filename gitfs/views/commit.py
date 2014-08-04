import os
from stat import S_IFDIR, S_IFREG, S_IFLNK
from pygit2 import (
    GIT_FILEMODE_TREE, GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE,
    GIT_FILEMODE_LINK
)

from log import log
from .view import View


class CommitView(View):

    def _get_git_object_type(self, tree, entry_name):
        for e in tree:
            if e.name == entry_name:
                return e.filemode
            elif e.filemode == GIT_FILEMODE_TREE:
                return self._get_git_object_type(self.repo[e.id], entry_name)

    def _get_blob_content(self, tree, blob_name):
        for node in tree:
            if node.name == blob_name:
                return self.repo[node.id].data
            elif node.filemode == GIT_FILEMODE_TREE:
                return self._get_blob_content(self.repo[node.id], blob_name)


    def readlink(self, path):
        commit = self.repo.revparse_single(self.commit_sha1)
        obj_name = os.path.split(path)[1]
        return self._get_blob_content(commit.tree, obj_name)

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        # TODO:
        #   * treat blob and blob_executable differently
        if path and path != '/':
            commit = self.repo.revparse_single(self.commit_sha1)
            obj_name = os.path.split(path)[1]
            obj_type = self._get_git_object_type(commit.tree, obj_name)
            if obj_type == GIT_FILEMODE_LINK:
                return dict(st_mode=(S_IFLNK | 0644))
            if obj_type == GIT_FILEMODE_BLOB or\
               obj_type == GIT_FILEMODE_BLOB_EXECUTABLE:
                return dict(st_mode=(S_IFREG | 0644))
            elif obj_type == GIT_FILEMODE_TREE:
                return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
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

