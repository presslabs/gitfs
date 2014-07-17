from fuse import Operations

from .view import View


class IndexView(View, Operations):
    def readdir(self, path, fh):
        print "I'm reading dirs"

    def utimens(self, path, a):
        print path, a

    def open(self, path, argument):
        print path, argument
