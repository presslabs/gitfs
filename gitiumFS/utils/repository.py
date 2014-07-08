from pygit2 import (Repository, clone_repository, GIT_CHECKOUT_SAFE_CREATE,
                    Signature)


class Repository(Repository):
  def push(self, upstream, branch):
    remote = self.get_remote(upstream)
    remote.push("refs/remotes/%s/%s" % (upstream, branch))

  def pull(self):
    pass

  def commit(self, message, author, author_email, ref="refs/heads/master"):
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
    return repo

  def get_remote(self, name):
    remote = [remote for remote in self._repo.remotes
              if remote.name == name]
    if not remote:
      raise ValueError("Missing remote")

    return remote[0]
