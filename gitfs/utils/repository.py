from pygit2 import (Repository as _Repository, clone_repository,
                    GIT_CHECKOUT_SAFE_CREATE, Signature, GIT_BRANCH_REMOTE,
                    GIT_CHECKOUT_FORCE, GIT_FILEMODE_TREE, GIT_FILEMODE_BLOB,
                    GIT_FILEMODE_BLOB_EXECUTABLE, GIT_FILEMODE_LINK)

from .path import split_path_into_components

class Repository(_Repository):

    def push(self, upstream, branch):
        """ Push changes from a branch to a remote

        Examples::

                repo.push("origin", "master")
        """

        remote = self.get_remote(upstream)
        remote.push("refs/remotes/%s/%s" % (upstream, branch))

    def pull(self, upstream, branch_name):
        """ Fetch from a remote and merge the result in local HEAD.

        Examples::

                repo.pull("origin", "master")
        """

        # fetch from remote
        remote = self.get_remote(upstream)
        remote.fetch()

        # merge with new changes
        branch = self.lookup_branch("%s/%s" % (upstream, branch_name),
                                    GIT_BRANCH_REMOTE)
        self.merge(branch.target)
        self.create_reference("refs/heads/%s" % branch_name,
                              branch.target, force=True)

        # TODO: get commiter from env
        # create commit
        commit = self.commit("Merging", "Vlad", "vladtemian@gmail.com")

        # update head to newly created commit
        self.create_reference("refs/heads/%s" % branch_name,
                              commit, force=True)
        self.checkout_head(GIT_CHECKOUT_FORCE)

        # cleanup the merging state
        self.clean_state_files()

    def commit(self, message, author, author_email, ref="HEAD"):
        """ Wrapper for create_commit. It creates a commit from a given ref
        (default is HEAD)
        """
        # sign the author
        commit_author = Signature(author, author_email)
        commiter = Signature(author, author_email)

        # write index localy
        tree = self.index.write_tree()
        self.index.write()

        # get parent
        parent = self.revparse_single(ref)
        return self.create_commit(ref, commit_author, commiter, message,
                                  tree, [parent.id])

    @classmethod
    def clone(cls, remote_url, path, branch=None):
        """Clone a repo in a give path and update the working directory with
        a checkout to head (GIT_CHECKOUT_SAFE_CREATE)

        :param str remote_url: URL of the repository to clone

        :param str path: Local path to clone into

        :param str branch: Branch to checkout after the
        clone. The default is to use the remote's default branch.

        """

        repo = clone_repository(remote_url, path, checkout_branch=branch)
        repo.checkout_head(GIT_CHECKOUT_SAFE_CREATE)
        return cls(path)

    def get_remote(self, name):
        """ Retrieve a remote by name. Raise a ValueError if the remote was not
        added to repo

        Examples::

                repo.get_remote("fork")
        """
        remote = [remote for remote in self.remotes
                  if remote.name == name]
        if not remote:
            raise ValueError("Missing remote")

        return remote[0]

    def _get_git_object_type(self, tree, entry_name, path_components):
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
            if (entry.name == entry_name and\
                len(path_components) == 1 and\
                entry.name == path_components[0]):

                return entry.filemode
            elif entry.filemode == GIT_FILEMODE_TREE:
                filemode = self._get_git_object_type(self[entry.id],
                                                     entry_name,
                                                     path_components[1:])
                if filemode:
                    return filemode

        return filemode

    def get_git_object_type(self, tree, path):
        path_components = split_path_into_components(path)
        return self._get_git_object_type(tree, path_components[-1],
                                         path_components)

    def _get_git_object(self, tree, obj_name, path_components):
        git_obj = None
        for entry in tree:
            if (entry.name == obj_name and\
                len(path_components) == 1 and\
                entry.name == path_components[0]):
                return self[entry.id]
            elif entry.filemode == GIT_FILEMODE_TREE:
                git_obj = self._get_git_object(self[entry.id],
                                                obj_name,
                                                path_components[1:])
                if git_obj:
                    return git_obj

        return git_obj


    def get_git_object(self, tree, path):
        path_components = split_path_into_components(path)
        return self._get_git_object(tree, path_components[-1], path_components)

    def get_blob_size(self, tree, path):
        return self.get_git_object(tree, path).size

    def get_blob_data(self, tree, path):
        return self.get_git_object(tree, path).data
