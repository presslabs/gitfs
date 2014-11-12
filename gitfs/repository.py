# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from collections import namedtuple
from stat import S_IFDIR, S_IFREG, S_IFLNK

from pygit2 import (clone_repository, Signature, GIT_SORT_TOPOLOGICAL,
                    GIT_FILEMODE_TREE, GIT_STATUS_CURRENT,
                    GIT_FILEMODE_LINK, GIT_FILEMODE_BLOB, GIT_BRANCH_REMOTE,
                    GIT_BRANCH_LOCAL, GIT_FILEMODE_BLOB_EXECUTABLE)
from gitfs.cache import CommitCache
from gitfs.utils.path import split_path_into_components
from gitfs.utils.commits import CommitsList


DivergeCommits = namedtuple("DivergeCommits", ["common_parent",
                            "first_commits", "second_commits"])


class Repository(object):

    def __init__(self, repository, commits=None):
        self._repo = repository
        self.commits = commits or CommitCache(self)

        self.behind = False

    def __getitem__(self, item):
        """
        Proxy method for pygit2.Repository
        """

        return self._repo[item]

    def __getattr__(self, attr):
        """
        Proxy method for pygit2.Repository
        """

        if attr not in self.__dict__:
            return getattr(self._repo, attr)
        else:
            return self.__dict__[attr]

    def ahead(self, upstream, branch):
        ahead, _ = self.diverge(upstream, branch)
        return ahead

    def diverge(self, upstream, branch):
        reference = "%s/%s" % (upstream, branch)
        remote_branch = self.lookup_branch(reference, GIT_BRANCH_REMOTE)
        local_branch = self.lookup_branch(branch, GIT_BRANCH_LOCAL)

        if remote_branch.target == local_branch.target:
            return False, False

        diverge_commits = self.find_diverge_commits(local_branch,
                                                    remote_branch)
        behind = len(diverge_commits.second_commits) > 0
        ahead = len(diverge_commits.first_commits) > 0

        return ahead, behind

    def checkout(self, ref, *args, **kwargs):
        result = self._repo.checkout(ref, *args, **kwargs)

        # update ignore cache after a checkout
        self.ignore.update()

        status = self._repo.status()
        for path, status in status.iteritems():
            # path is in current status, move on
            if status == GIT_STATUS_CURRENT:
                continue

            # check if file exists or not
            if path not in self._repo.index:
                if path not in self.ignore:
                    os.unlink(self._full_path(path))
                continue

            # check files stats
            stats = self.get_git_object_default_stats(ref, path)
            current_stat = os.lstat(self._full_path(path))

            if stats['st_mode'] != current_stat.st_mode:
                os.chmod(self._full_path(path), current_stat.st_mode)
                self._repo.index.add(self._sanitize(path))

        return result

    def _sanitize(self, path):
        if path is not None and path.startswith("/"):
            path = path[1:]
        return path

    def push(self, upstream, branch):
        """ Push changes from a branch to a remote

        Examples::

                repo.push("origin", "master")
        """

        remote = self.get_remote(upstream)
        remote.push("refs/heads/%s" % (branch))

    def fetch(self, upstream, branch_name):
        """
        Fetch from remote and return True if we are behind or False otherwise
        """

        remote = self.get_remote(upstream)
        remote.fetch()

        _, behind = self.diverge(upstream, branch_name)
        self.behind = behind

    def commit(self, message, author, commiter, parents=None, ref="HEAD"):
        """ Wrapper for create_commit. It creates a commit from a given ref
        (default is HEAD)
        """

        status = self._repo.status()
        if status == {}:
            return None

        # sign the author
        author = Signature(author[0], author[1])
        commiter = Signature(commiter[0], commiter[1])

        # write index localy
        tree = self._repo.index.write_tree()
        self._repo.index.write()

        # get parent
        if parents is None:
            parents = [self._repo.revparse_single(ref).id]

        return self._repo.create_commit(ref, author, commiter, message,
                                        tree, parents)

    @classmethod
    def clone(cls, remote_url, path, branch=None, credentials=None):
        """Clone a repo in a give path and update the working directory with
        a checkout to head (GIT_CHECKOUT_SAFE_CREATE)

        :param str remote_url: URL of the repository to clone

        :param str path: Local path to clone into

        :param str branch: Branch to checkout after the
        clone. The default is to use the remote's default branch.

        """

        repo = clone_repository(remote_url, path, checkout_branch=branch,
                                credentials=credentials)
        repo.checkout_head()
        return cls(repo)

    def _is_searched_entry(self, entry_name, searched_entry, path_components):
        """
        Checks if a tree entry is the one that is being searched for. For
        that, the name has to correspond and it has to be the last element
        in the path_components list (this means that the path corresponds
        exactly).

        :param entry_name: the name of the tree entry
        :param searched_entry: the name of the object that is being searched
                               for
        :type searched_entry: str
        :param path_components: the path of the object being searched for
        :type path_components: list
        """

        return (entry_name == searched_entry and
                len(path_components) == 1 and
                entry_name == path_components[0])

    def _get_git_object(self, tree, obj_name, path_components, modifier):
        """
        It recursively searches for the object in the repository. To declare
        an object as found, the name and the relative path have to correspond.
        It also includes the relative path as a condition for success, to avoid
        finding an object with the correct name but with a wrong location.

        :param tree: a `pygit2.Tree` instance
        :param entry_name: the name of the object
        :type entry_name: str
        :param path_components: the path of the object being searched for as
            a list (e.g: for '/a/b/c/file.txt' => ['a', 'b', 'c', 'file.txt'])
        :type path_components: list
        :param modifier: a function used to retrieve some specific
            characteristic of the git object
        :type modifier: function
        :returns: an instance corresponding to the object that is being
            searched for in case of success, or None otherwise.
        :rtype: one of the following:
            an instance of `pygit2.Tree`
            an instance of `pygit2.Blob`
            None
        """

        git_obj = None
        for entry in tree:
            if self._is_searched_entry(entry.name, obj_name, path_components):
                return modifier(entry)
            elif entry.filemode == GIT_FILEMODE_TREE:
                git_obj = self._get_git_object(self._repo[entry.id], obj_name,
                                               path_components[1:], modifier)
                if git_obj:
                    return git_obj

        return git_obj

    def get_git_object_type(self, tree, path):
        """
        Returns the filemode of the git object with the relative path <path>.

        :param tree: a `pygit2.Tree` instance
        :param path: the relative path of the object
        :type entry_name: str
        :returns: the filemode for the entry in case of success
            (which can be one of the following) or None otherwise.
            0     (0000000)  GIT_FILEMODE_NEW
            16384 (0040000)  GIT_FILEMODE_TREE
            33188 (0100644)  GIT_FILEMODE_BLOB
            33261 (0100755)  GIT_FILEMODE_BLOB_EXECUTABLE
            40960 (0120000)  GIT_FILEMODE_LINK
            57344 (0160000)  GIT_FILEMODE_COMMIT
        :rtype: int, None
        """

        path_components = split_path_into_components(path)
        try:
            return self._get_git_object(tree, path_components[-1],
                                        path_components,
                                        lambda entry: entry.filemode)
        except:
            return GIT_FILEMODE_TREE

    def get_git_object(self, tree, path):
        """
        Returns the git object with the relative path <path>.

        :param tree: a `pygit2.Tree` instance
        :param path: the relative path of the object
        :type path: str
        :returns: an instance corresponding to the object that is being
            searched for in case of success, or None else.
        :rtype: one of the following:
            an intance of `pygit2.Tree`
            an intance of `pygit2.Blob`
            None
        """

        # It acts as a proxy for the _get_git_object method, which
        # does the actual searching.
        path_components = split_path_into_components(path)
        return self._get_git_object(tree, path_components[-1], path_components,
                                    lambda entry: self._repo[entry.id])

    def get_git_object_default_stats(self, ref, path):
        types = {
            GIT_FILEMODE_LINK: {'st_mode': S_IFLNK | 0444},
            GIT_FILEMODE_TREE: {'st_mode': S_IFDIR | 0555, 'st_nlink': 2},
            GIT_FILEMODE_BLOB: {'st_mode': S_IFREG | 0444},
            GIT_FILEMODE_BLOB_EXECUTABLE: {'st_mode': S_IFREG | 0555},
        }

        if path == "/":
            return types[GIT_FILEMODE_TREE]

        obj_type = self.get_git_object_type(ref, path)
        if obj_type is None:
            return obj_type

        stats = types[obj_type]
        if obj_type in [GIT_FILEMODE_BLOB, GIT_FILEMODE_BLOB_EXECUTABLE]:
            stats['st_size'] = self.get_blob_size(ref, path)

        return stats

    def get_blob_size(self, tree, path):
        """
        Returns the size of a the data contained by a blob object
        with the relative path <path>.

        :param tree: a `pygit2.Tree` instance
        :param path: the relative path of the object
        :type path: str
        :returns: the size of data contained by the blob object.
        :rtype: int
        """
        return self.get_git_object(tree, path).size

    def get_blob_data(self, tree, path):
        """
        Returns the data contained by a blob object with the relative
        path <path>.

        :param tree: a `pygit2.Tree` instance
        :param path: the relative path of the object
        :type path: str
        :returns: the data contained by the blob object.
        :rtype: str
        """
        return self.get_git_object(tree, path).data

    def get_commit_dates(self):
        """
        Walk through all commits from current repo in order to compose the
        _history_ directory.
        """
        return self.commits.keys()

    def get_commits_by_date(self, date):
        """
        Retrieves all the commits from a particular date.

        :param date: date with the format: yyyy-mm-dd
        :type date: str
        :returns: a list containg the commits for that day. Each list item
            will have the format: hh:mm:ss-<short_sha1>, where short_sha1 is
            the short sha1 of the commit (first 10 characters).
        :rtype: list
        """
        return map(str, self.commits[date])

    def walk_branches(self, sort, *branches):
        """
        Simple iterator which take a sorting strategy and some branch and
        iterates through those branches one commit at a time, yielding a list
        of commits

        :param sort: a sorting option `GIT_SORT_NONE, GIT_SORT_TOPOLOGICAL,
        GIT_SORT_TIME, GIT_SORT_REVERSE`. Default is 'GIT_SORT_TOPOLOGICAL'
        :param branches: branch to iterate through
        :type branches: list
        :returns: yields a list of commits corresponding to given branches
        :rtype: list

        """

        iterators = [self._repo.walk(branch.target, sort)
                     for branch in branches]
        stop_iteration = [False for branch in branches]

        commits = []
        for iterator in iterators:
            try:
                commit = iterator.next()
            except StopIteration:
                commit = None
            commits.append(commit)

        yield (commit for commit in commits)

        while not all(stop_iteration):
            for index, iterator in enumerate(iterators):
                try:
                    commit = iterator.next()
                    commits[index] = commit
                except StopIteration:
                    stop_iteration[index] = True

            if not all(stop_iteration):
                yield (commit for commit in commits)

    def remote_head(self, upstream, branch):
        ref = "%s/%s" % (upstream, branch)
        remote = self._repo.lookup_branch(ref, GIT_BRANCH_REMOTE)
        return remote.get_object()

    def get_remote(self, name):
        """ Retrieve a remote by name. Raise a ValueError if the remote was not
        added to repo

        Examples::

                repo.get_remote("fork")
        """

        remote = [remote for remote in self._repo.remotes
                  if remote.name == name]

        if not remote:
            raise ValueError("Missing remote")

        if hasattr(self, 'credentials'):
            remote[0].credentials = self.credentials

        return remote[0]

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        return os.path.join(self._repo.workdir, partial)

    def find_diverge_commits(self, first_branch, second_branch):
        """
        Take two branches and find diverge commits.

             2--3--4--5
            /
        1--+              Return:
            \               - common parent: 1
             6              - first list of commits: (2, 3, 4, 5)
                            - second list of commits: (6)

        :param first_branch: first branch to look for common parent
        :type first_branch: `pygit2.Branch`
        :param second_branch: second branch to look for common parent
        :type second_branch: `pygit2.Branch`
        :returns: a namedtuple with common parent, a list of first's branch
        commits and another list with second's branch commits
        :rtype: DivergeCommits (namedtuple)
        """

        common_parent = None
        first_commits = CommitsList()
        second_commits = CommitsList()

        walker = self.walk_branches(GIT_SORT_TOPOLOGICAL,
                                    first_branch, second_branch)

        for first_commit, second_commit in walker:
            if (first_commit in second_commits or
               second_commit in first_commits):
                break

            if first_commit not in first_commits:
                first_commits.append(first_commit)
            if second_commit not in second_commits:
                second_commits.append(second_commit)

            if second_commit.hex == first_commit.hex:
                break

        if first_commit in second_commits:
            index = second_commits.index(first_commit)
            second_commits = second_commits[:index]
            common_parent = first_commit

        if second_commit in first_commits:
            index = first_commits.index(second_commit)
            first_commits = first_commits[:index]
            common_parent = second_commit

        return DivergeCommits(common_parent, first_commits, second_commits)
