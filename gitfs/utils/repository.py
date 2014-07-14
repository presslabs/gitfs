from pygit2 import (Repository as _Repository, clone_repository,
                    GIT_CHECKOUT_SAFE_CREATE, Signature, GIT_BRANCH_REMOTE,
                    GIT_CHECKOUT_FORCE)


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
  def clone(cls, remote_url, path):
    """Clone a repo in a give path and update the working directory with
    a checkout to head (GIT_CHECKOUT_SAFE_CREATE)
    """

    repo = clone_repository(remote_url, path)
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
