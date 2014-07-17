import os

from fuse import Operations

from .view import View


class IndexView(View, Operations):
    def readdir(self, path, fh):
        print "I'm reading dirs"

    def utimens(self, path, a):
        print path, a

    def open(self, path, argument):
        print path, argument

    def build_paths(self, root=''):
        """ Get all paths from repos. Hold them in memory.
        """
        full_path = self._full_path(self.repo_path, root)
        paths = {'.': {}, '..': {}}

        items = os.listdir(full_path)
        for item in items:
            if os.path.isdir("%s/%s" % (full_path, item)):
                paths[item] = self.build_paths("%s%s/" % (root, item))
            else:
                paths[item] = {}

        return paths
