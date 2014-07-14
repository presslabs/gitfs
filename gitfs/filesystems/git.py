import re

from gitfs.utils import Repository

from .passthrough import PassthroughFuse


class GitFuse(PassthroughFuse):
  def __init__(self, remote_url, repos_path):
    self.remote_url = remote_url
    self.root = self._get_root(repos_path)

    self.repo = Repository.clone(remote_url, self.root)

  def _get_root(self, repos_path):
    match = re.search(r"(?P<repo_name>[A-Za-z0-9]+)\.git", self.remote_url)
    return "%s/%s" % (repos_path, match.group("repo_name"))

  def write(self, path, buff, offset, fh):
    result = super(GitFuse, self).write(path, buff, offset, fh)

    self.repo.index.add(path)
    self.repo.commit("Test commit", "gitFS", "git@fs.com")
    self.repo.push("origin", "master")

    return result
