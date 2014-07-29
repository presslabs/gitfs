import os
from abc import ABCMeta, abstractmethod

from gitfs import  FuseMethodNotImplemented
from gitfs.filesystems.passthrough import PassthroughFuse

class View(PassthroughFuse):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.args = args

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])


    def getxattr(self, path, name, position=0):
        """Get extended attributes"""

        raise FuseMethodNotImplemented
