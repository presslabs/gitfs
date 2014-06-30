import re
from gitiumFS import default_config

from .passthrough import PassthroughFuse


class GitFuse(PassthroughFuse):
  def __init__(self, remote_url):
    self.remote_url = remote_url
    self.root = self._get_root()

  def _get_root(self):
    print self.remote_url
    match = re.search(r"(?P<repo_name>[A-Za-z0-9]+)\.git", self.remote_url)
    return "%s/%s" % (default_config.repos_path, match.group("repo_name"))
