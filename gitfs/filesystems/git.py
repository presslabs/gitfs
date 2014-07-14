import os
import re
import shutil
import signal

from gitfs.utils import Repository

from .passthrough import PassthroughFuse


class GitFuse(PassthroughFuse):
  def __init__(self, remote_url, repos_path):
    self.remote_url = remote_url
    self.root = self._get_root(repos_path)
    self.repos = repos_path

    self.repo = Repository.clone(remote_url, self.root)

    self._paths = {
        'current': self.current(),
        'history': self.history,
    }

    signal.signal(signal.SIGTERM, self.on_SIGTERM)

  def current(self, path=''):
    full_path = self._full_path(path)
    paths = {}

    items = os.listdir(full_path)
    for item in items:
      if os.path.isdir("%s/%s" % (full_path, item)):
        paths[item] = self.current("%s%s/" % (path, item))

    return paths

  def readdir(self, path, fh):
    path = path.split('/')
    paths = self._paths

    for entry in path:
      # TODO: raise not found
      if entry and entry in paths:
        paths = paths[entry]

    # TODO: check for file
    for item in paths.keys():
      yield item

  @property
  def history(self):
    return {"not_yet_implemented": {}}

  def _get_root(self, repos_path):
    match = re.search(r"(?P<repo_name>[A-Za-z0-9]+)\.git", self.remote_url)
    return "%s/%s" % (repos_path, match.group("repo_name"))

  def write(self, path, buff, offset, fh):
    result = super(GitFuse, self).write(path, buff, offset, fh)

    self.repo.index.add(path)
    self.repo.commit("Test commit", "gitFS", "git@fs.com")
    self.repo.push("origin", "master")

    return result

  def on_SIGTERM(self):
    shutil.rmtree("%s/%s" % (self.repos, self.root))
