from abc import ABCMeta

from gitfs import FuseMethodNotImplemented


class View(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.args = args

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def getattr(self, *args, **kwargs):
        return {
            'st_uid': self.uid,
            'st_gid': self.gid,
        }

    def getxattr(self, path, fh):
        raise FuseMethodNotImplemented
