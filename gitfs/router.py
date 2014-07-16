from gitfs.filesystems import GitFS


class Router(GitFS):
  def __init__(self, remote_url, repos_path, branch=None):
    """
    Clone repo from a remote into repos_path/<repo_name> and checkout to
    a specific branch.

    :param str remote_url: URL of the repository to clone

    :param str repos_path: Where are all the repos clonedd

    :param str branch: Branch to checkout after the
    clone. The default is to use the remote's default branch.

    """
    super(Router, self).__init__(remote_url, repos_path, branch)

    self.routes = []

  def register(self, regex, cls):
    self.routes.append(regex, cls)

  def get_view(self):
    print 'ok'
