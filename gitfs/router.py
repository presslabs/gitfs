import re
import inspect
from fuse import Operations

from gitfs.utils import Repository


class Router(object):
    def __init__(self, remote_url, repos_path, branch=None):
        """
        Clone repo from a remote into repos_path/<repo_name> and checkout to
        a specific branch.

        :param str remote_url: URL of the repository to clone
        :param str repos_path: Where are all the repos clonedd
        :param str branch: Branch to checkout after the
        clone. The default is to use the remote's default branch.

        """
        self.remote_url = remote_url
        self.repo_path = self._get_repo(repos_path)
        self.repos = repos_path
        self.operations = Operations()

        self.repo = Repository.clone(remote_url, self.repo_path, branch)

        self.routes = []

    def register(self, regex, view):
        self.routes.append({
            'regex': regex,
            'view': view
        })

    def get_view(self, path):
        """
        Try to map a given path to it's specific view.

        If a match is found, an view object is created with the right regex
        groups(named or unnamed).

        :param str path: path to be matched
        :rtype: view object, relative path
        """

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
        """Magic method which, return a specific method from a view.

        In Fuse API, almost each method receive a path argument. Based on that
        path we can route each call to a specific view. For example, if a
        method which has a path argument like `/current/dir1/dir2/file1` is
        called, we need to get the certain view that will know how to handle
        this path, instantiate it and then call our method on the new created
        object`

        :params str attr_name: Method name to be called
        :rtype: function
        """

        if attr_name not in dir(self.operations):
            message = 'Method %s is not implemented by this FS' % attr_name
            raise NotImplementedError(message)

        attr = getattr(self.operations, attr_name)
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

    def _get_repo(self, repos_path):
        match = re.search(r"(?P<repo_name>[\w\-\_]+)\.git", self.remote_url)
        return "%s/%s" % (repos_path, match.group("repo_name"))
