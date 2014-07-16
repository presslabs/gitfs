import re

from fuse import Operations, LoggingMixIn

from gitfs.utils import Repository


class GitFS(LoggingMixIn, Operations):
  def __init__(self, remote_url, repos_path, branch=None):
    self.remote_url = remote_url
    self.root = self._get_root(repos_path)
    self.repos = repos_path

    self.repo = Repository.clone(remote_url, self.root, branch)

  def _get_root(self, repos_path):
    match = re.search(r"(?P<repo_name>[A-Za-z0-9]+)\.git", self.remote_url)
    return "%s/%s" % (repos_path, match.group("repo_name"))
