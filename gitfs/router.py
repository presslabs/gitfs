import re
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

    def register(self, regex, view):
        self.routes.append({
            'regex': regex,
            'view': view
        })

    def get_view(self, path):
        for route in self.routes:
            result = re.search(route['regex'], path)
            if result is None:
                continue

            groups = result.groups()
            relative_path = re.sub(route['regex'], '', path)

            kwargs = result.groupdict()
            args = set(groups) - set(kwargs.values())

            return route['view'](*args, **kwargs), relative_path

        raise ValueError("View not found!")

    def __getattr__(self, attr_name):
        if attr_name not in dir(operations):
            message = 'Method %s is not implemented by this FS' % attr_name
            raise NotImplementedError(message)

        attr = getattr(operations, attr_name)
        if not callable(attr):
            raise ValueError('Invalid method')

        args = inspect.getargspec(attr).args
        if 'path' not in args:
            # TODO: route to special methods
            raise Exception('route to special methods')

        def placeholder(path, *arg, **kwargs):
            view, relative_path = self.get_view(path)
            method = getattr(view, attr_name)
            return method(relative_path, *arg, **kwargs)

        return placeholder
