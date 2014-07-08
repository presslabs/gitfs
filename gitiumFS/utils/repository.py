from pygit2 import Repository, clone_repository, GIT_CHECKOUT_SAFE_CREATE


class Repository(Repository):
  def push(self):
    pass

  def pull(self):
    pass

  def commit(self):
    pass

  @classmethod
  def clone(cls, remote_url, path):
    repo = clone_repository(remote_url, path)
    repo.checkout_head(GIT_CHECKOUT_SAFE_CREATE)
    return repo
