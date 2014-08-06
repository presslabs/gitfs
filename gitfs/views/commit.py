import os
from collections import deque
from stat import S_IFDIR, S_IFREG, S_IFLNK
from errno import ENOENT
from pygit2 import (
    GIT_FILEMODE_TREE, GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE,
    GIT_FILEMODE_LINK
)
from fuse import FuseOSError

from .view import View


class CommitView(View):

    def __init__(self, *args, **kwargs):
        super(CommitView, self).__init__(*args, **kwargs)

        try:
            self.commit = self.repo.revparse_single(self.commit_sha1)
        except KeyError:
            raise FuseOSError(ENOENT)

    def _get_git_object_type(self, tree, entry_name):
        """
        Returns the filemode of the git object with the name <entry_name>.


        Available fielmodes:

         0     (0000000)  GIT_FILEMODE_NEW
         16384 (0040000)  GIT_FILEMODE_TREE
         33188 (0100644)  GIT_FILEMODE_BLOB
         33261 (0100755)  GIT_FILEMODE_BLOB_EXECUTABLE
         40960 (0120000)  GIT_FILEMODE_LINK
         57344 (0160000)  GIT_FILEMODE_COMMIT

        :param tree: a pygit2.Tree instance
        :param entry_name: the name of the entry that is being searched for
        :type entry_name: str
        :returns: the filemode for the entry :rtype: int
        """

        filemode = None
        for entry in tree:
            if entry.name == entry_name:
                return entry.filemode
            elif entry.filemode == GIT_FILEMODE_TREE:
                filemode = self._get_git_object_type(self.repo[entry.id],
                                                     entry_name)
                if filemode:
                    return filemode

        return filemode

    def _get_blob_size(self, tree, blob_name):
        return self._get_blob(tree, blob_name).size

    def _get_blob_content(self, tree, blob_name):
        return self._get_blob(tree, blob_name).data

    def _get_blob(self, tree, blob_name):
        """
        Returns the content of a Blob object with the name <blob_name>.

        :param tree: a commit tree or a simple tree
        :param blob_name: the name of the blob that is being searched for
        :type blob_name: str
        :returns: the content of the blob with the name <blob_name>
        :rtype: str
        """
        for node in tree:
            if node.name == blob_name:
                return self.repo[node.id]
            elif node.filemode == GIT_FILEMODE_TREE:
                return self._get_blob(self.repo[node.id], blob_name)

    def _split_path_into_components(self, path):
        """
        Splits a path and returns a list of its constituents.
        E.g.: /totally/random/path => ['totally', 'random', 'path']

        :param path: the path to be split
        :type path: str
        :returns: the list which contains the path components
        """
        head, tail = os.path.split(path)
        if not tail:
            return []

        components = deque()
        components.appendleft(tail)

        path = head

        while path != '/':
            head, tail = os.path.split(path)
            components.appendleft(tail)
            path = head

        return list(components)

    def _validate_commit_path(self, tree, path_components):
        """
        Checks if a particular path is valid in the context of the commit
        which is being browsed.

        :param tree: a commit tree or a pygit2 tree
        :param path_components: the components of the path to be checked
            as a list (e.g.: ['totally', 'random', 'path'])
        :type path_components: list
        :returns: True if the path is valid, False otherwise
        """

        for entry in tree:
            if (entry.name == path_components[0] and
               entry.filemode == GIT_FILEMODE_TREE and
               len(path_components) == 1):
                return True
            elif (entry.name == path_components[0] and
                  entry.filemode == GIT_FILEMODE_TREE and
                  len(path_components) > 1):
                return self._validate_commit_path(self.repo[entry.id],
                                                  path_components[1:])

        return False

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

    def read(self, path, size, offset, fh):
        obj_name = os.path.split(path)[1]
        content = self._get_blob_content(self.commit.tree, obj_name)
        return content[offset:offset + size]

    def open(self, path, flags):
        return 0

    def readlink(self, path):
        obj_name = os.path.split(path)[1]
        return self._get_blob_content(self.commit.tree, obj_name)

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        if not path:
            return

        attrs = super(CommitView, self).getattr(path, fh)

        types = {
            GIT_FILEMODE_LINK: {'st_mode': S_IFLNK | 0644},
            GIT_FILEMODE_TREE: {'st_mode': S_IFDIR | 0644, 'st_nlink': 2},
            GIT_FILEMODE_BLOB: {'st_mode': S_IFREG | 0644},
            GIT_FILEMODE_BLOB_EXECUTABLE: {'st_mode': S_IFREG | 0755},
        }

        if path == '/':
            attrs.update(types[GIT_FILEMODE_TREE])
        else:
            obj_name = os.path.split(path)[1]
            obj_type = self._get_git_object_type(self.commit.tree, obj_name)

            if obj_type is None:
                raise FuseOSError(ENOENT)

            attrs.update(types[obj_type])
            if obj_type in [GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE]:
                attrs['st_size'] = self._get_blob_size(self.commit.tree,
                                                       obj_name)

        return attrs

    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        """
        Check if the relative path is a valid path in the context of the
        commit that is being browsed. If not, raise Fuseoserror with
        """

        if self.relative_path and self.relative_path != '/':
            path_elems = self._split_path_into_components(self.relative_path)
            is_valid_path = self._validate_commit_path(self.commit.tree,
                                                       path_elems)
            if not is_valid_path:
                raise FuseOSError(ENOENT)

        return 0

    def readdir(self, path, fh):
        dir_tree = self.commit.tree

        # If the relative_path is not empty, fetch the git tree corresponding
        # to the directory that we are in.
        tree_name = os.path.split(self.relative_path)[1]
        if tree_name:
            subtree = self._get_commit_subtree(self.commit.tree, tree_name)
            dir_tree = subtree

        return ['.', '..'] + [entry.name for entry in dir_tree]

    def flush(self, path, fh):
        return 0

    def release(self, path, fh):
        return 0
