from pygit2 import (clone_repository, Signature, GIT_FILEMODE_TREE,
                    GIT_BRANCH_REMOTE)

from gitfs.cache import CommitCache
from gitfs.utils.path import split_path_into_components


class Repository(object):

    def __init__(self, repository, commits=None):
        self._repo = repository
        self.commits = commits or CommitCache(self)

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

        remote_commit = self.remote_head(upstream, branch_name)

        remote = self.get_remote(upstream)
        remote.fetch()

        new_remote_commit = self.remote_head(upstream, branch_name)

        if remote_commit.hex != new_remote_commit.hex:
            return True

        return False

    def commit(self, message, author, commiter, parents=None, ref="HEAD"):
        """ Wrapper for create_commit. It creates a commit from a given ref
        (default is HEAD)
        """

        status = self._repo.status()
        if not status:
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

    def _get_git_object_type(self, tree, entry_name, path_components):
        """
        It recursively searches for the object in the repository. To declare
        an object as found, the name and the relative path have to correspond.
        It also includes the relative path as a condition for success to avoid
        finding an object with the correct name but with a wrong location.

        :param tree: a `pygit2.Tree` instance
        :param entry_name: the name of the object
        :type entry_name: str
        :param path_components: the path of the object being searched for as
            a list (e.g: for '/a/b/c/file.txt' => ['a', 'b', 'c', 'file.txt'])
        :type path_components: list
        :returns: the filemode for the entry
        :rtype: int
        """

        filemode = None
        for entry in tree:
            if self._is_searched_entry(entry.name, entry_name,
                                       path_components):
                return entry.filemode
            elif entry.filemode == GIT_FILEMODE_TREE:
                filemode = self._get_git_object_type(self._repo[entry.id],
                                                     entry_name,
                                                     path_components[1:])
                if filemode:
                    return filemode

        return filemode

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

        # It acts as a proxy for the _get_git_object_type method, which
        # does the actual searching.
        path_components = split_path_into_components(path)
        try:
            return self._get_git_object_type(tree, path_components[-1],
                                             path_components)
        except:
            self.ignore.items.append(path)
            return GIT_FILEMODE_TREE

    def _get_git_object(self, tree, obj_name, path_components):
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
                return self._repo[entry.id]
            elif entry.filemode == GIT_FILEMODE_TREE:
                git_obj = self._get_git_object(self._repo[entry.id], obj_name,
                                               path_components[1:])
                if git_obj:
                    return git_obj

        return git_obj

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
        return self._get_git_object(tree, path_components[-1], path_components)

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

        iterators = [self._repo.walk(branch.target) for branch in branches]
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
                except:
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
