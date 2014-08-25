from abc import ABCMeta

from fuse import Operations, LoggingMixIn


class View(LoggingMixIn, Operations):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.args = args

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def getattr(self, *args, **kwargs):
        return {
            'st_uid': self.uid,
            'st_gid': self.gid,
            'st_ctime': self.mount_time,
            'st_mtime': self.mount_time,
        }
