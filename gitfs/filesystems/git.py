import os
import re
import shutil
import signal
from datetime import datetime

from pygit2 import GIT_SORT_TIME

from gitfs.utils import Repository

from .passthrough import PassthroughFuse


class GitFuse(PassthroughFuse):
  def __init__(self, remote_url, repos_path, branch=None):
    self.remote_url = remote_url
    self.root = self._get_root(repos_path)
    self.repos = repos_path

    self.repo = Repository.clone(remote_url, self.root, branch)

    self._paths = {
        'current': self.current(),
        'history': self.history(),
    }

    signal.signal(signal.SIGTERM, self.on_SIGTERM)

  def current(self, path=''):
    """ Get all paths from repos. Hold them in memory.
    """
    full_path = self._full_path(path)
    paths = {'.': {}, '..': {}}

    items = os.listdir(full_path)
    for item in items:
      if os.path.isdir("%s/%s" % (full_path, item)):
        paths[item] = self.current("%s%s/" % (path, item))
      else:
        paths[item] = {}

    return paths

  def readdir(self, path, fh):
    """ Because all our paths are in memory, it's very easy to read them. Just
    go through self._paths and that's it.
    """
    path = path.split('/')
    paths = self._paths

    for entry in path:
      # TODO: raise not found
      if entry and entry in paths:
        paths = paths[entry]

    if paths.keys():
      for item in paths.keys():
        yield item

  def getattr(self, path, fh=None):
    if path in ['/', '/current'] or path.startswith('/current'):
      path = path.replace('/current', '')
      return super(GitFuse, self).getattr(path, fh)
    elif path.startswith('/history'):
      print path

  def history(self):
    """ Walk through all commits from current repo in order to compose
    _history_ directory
    """
    paths = {}

    for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
      commit_time = datetime.fromtimestamp(commit.commit_time)

      day = "%s-%s-%s" % (commit_time.year, commit_time.month, commit_time.day)
      time = "%s-%s-%s" % (commit_time.hour, commit_time.minute,
                           commit_time.second)

      paths[day] = "%s-%s" % (time, commit.hex)

    return paths

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
