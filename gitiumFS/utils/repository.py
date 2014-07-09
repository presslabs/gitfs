from pygit2 import (Repository, clone_repository, GIT_CHECKOUT_SAFE_CREATE,
                    Signature, GIT_BRANCH_REMOTE, GIT_CHECKOUT_FORCE)


class Repository(Repository):
  def push(self, upstream, branch):
    remote = self.get_remote(upstream)
    remote.push("refs/remotes/%s/%s" % (upstream, branch))

  def pull(self, upstream, branch_name):
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

    self.create_reference("refs/heads/%s" % branch_name,
                          commit, force=True)
    self.checkout_head(GIT_CHECKOUT_FORCE)
    self.clean_state_files()

  def commit(self, message, author, author_email, ref="HEAD"):
    commit_author = Signature(author, author_email)
    commiter = Signature(author, author_email)

    tree = self.index.write_tree()
    self.index.write()

    parent = self.revparse_single(ref)
    return self.create_commit(ref, commit_author, commiter, message,
                              tree, [parent.id])

  @classmethod
  def clone(cls, remote_url, path):
    repo = clone_repository(remote_url, path)
    repo.checkout_head(GIT_CHECKOUT_SAFE_CREATE)
    return cls(repo)

  def get_remote(self, name):
    remote = [remote for remote in self.remotes
              if remote.name == name]
    if not remote:
      raise ValueError("Missing remote")

    return remote[0]
