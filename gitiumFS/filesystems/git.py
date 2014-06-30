
from .passthrough import PassthroughFuse


class GitFuse(PassthroughFuse):
  def __init__(self, remote_url):
    self.remote_url = remote_url
    self.root = "repo"
