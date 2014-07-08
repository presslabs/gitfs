from pygit2 import (Repository, clone_repository, GIT_CHECKOUT_SAFE_CREATE,
                    Signature)


class Repository(Repository):
  def push(self):
    pass

  def pull(self):
    pass

  def commit(self, message, author, author_email, ref="refs/heads/master"):
    commit_author = Signature(author, author_email)
    commiter = Signature(author, author_email)
    tree = self.TreeBuilder().write()
    parent = self.revparse_single(ref)
    return self.create_commit(ref, commit_author, commiter, tree, [parent])

  @classmethod
  def clone(cls, remote_url, path):
    repo = clone_repository(remote_url, path)
    repo.checkout_head(GIT_CHECKOUT_SAFE_CREATE)
    return repo
