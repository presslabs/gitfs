import inspect

from fuse import Operations

from gitfs.filesystems import GitFS


operations = Operations()


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
        # super(Router, self).__init__(remote_url, repos_path, branch)

        self.routes = []

    def register(self, regex, cls):
        self.routes.append((regex, cls))

    def get_view(self):
        print 'ok'

    def __getattr__(self, attr_name):
        if attr_name not in dir(operations):
            message = 'Method %s is not implemented by this FS' % attr_name
            raise NotImplemented(message)

        attr = getattr(operations, attr_name)
        if not callable(attr):
            raise ValueError('Invalid method')

        args = inspect.getargspec(attr).args
        if 'path' not in args:
            # TODO: route to special methods
            raise Exception('route to special methods')

        def placeholder(path, *arg, **kwargs):
            view = self.get_view(path)
            method = getattr(view, attr_name)
            return method(path, *arg, **kwargs)

        return placeholder
