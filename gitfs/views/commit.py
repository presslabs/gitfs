import os
from stat import S_IFDIR, S_IFREG, S_IFLNK
from errno import ENOENT
from pygit2 import (
    GIT_FILEMODE_TREE, GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE,
    GIT_FILEMODE_LINK
)
from fuse import FuseOSError

from gitfs.utils import split_path_into_components
from gitfs.cache import lru_cache

from .read_only import ReadOnlyView


class CommitView(ReadOnlyView):
    def __init__(self, *args, **kwargs):
        super(CommitView, self).__init__(*args, **kwargs)

        try:
            self.commit = self.repo.revparse_single(self.commit_sha1)
        except KeyError:
            raise FuseOSError(ENOENT)

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

        is_valid = False
        for entry in tree:
            if (entry.name == path_components[0] and
               entry.filemode == GIT_FILEMODE_TREE and
               len(path_components) == 1):
                return True
            elif (entry.name == path_components[0] and
                  entry.filemode == GIT_FILEMODE_TREE and
                  len(path_components) > 1):
                is_valid = self._validate_commit_path(self.repo[entry.id],
                                                      path_components[1:])
                if is_valid:
                    return is_valid

        return is_valid

    def read(self, path, size, offset, fh):
        data = self.repo.get_blob_data(self.commit.tree, path)
        return data[offset:offset + size]

    def readlink(self, path):
        obj_name = os.path.split(path)[1]
        return self.repo.get_blob_data(self.commit.tree, obj_name)

    @lru_cache(1000)
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
        attrs.update({
            'st_ctime': self.commit.commit_time,
            'st_mtime': self.commit.commit_time,
        })

        types = {
            GIT_FILEMODE_LINK: {'st_mode': S_IFLNK | 0444},
            GIT_FILEMODE_TREE: {'st_mode': S_IFDIR | 0555, 'st_nlink': 2},
            GIT_FILEMODE_BLOB: {'st_mode': S_IFREG | 0444},
            GIT_FILEMODE_BLOB_EXECUTABLE: {'st_mode': S_IFREG | 0555},
        }

        if path == '/':
            attrs.update(types[GIT_FILEMODE_TREE])
        else:
            obj_type = self.repo.get_git_object_type(self.commit.tree, path)

            if obj_type is None:
                raise FuseOSError(ENOENT)

            attrs.update(types[obj_type])
            if obj_type in [GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE]:
                attrs['st_size'] = self.repo.get_blob_size(self.commit.tree,
                                                           path)
        return attrs

    def access(self, path, amode):
        if self.relative_path and self.relative_path != '/':
            path_elems = split_path_into_components(self.relative_path)
            is_valid_path = self._validate_commit_path(self.commit.tree,
                                                       path_elems)
            if not is_valid_path:
                raise FuseOSError(ENOENT)

        return 0

    def readdir(self, path, fh):
        dir_tree = self.commit.tree

        # If the relative_path is not empty, fetch the git tree corresponding
        # to the directory that we are in.
        tree_name = os.path.split(path)[1]
        if tree_name:
            dir_tree = self.repo.get_git_object(self.commit.tree, path)

        dir_entries = ['.', '..'] + [entry.name for entry in dir_tree]
        for entry in dir_entries:
            yield entry
