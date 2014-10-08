from fuse import FuseOSError, ENOTSUP

FuseMethodNotImplemented = FuseOSError(ENOTSUP)

from gitfs.mounter import start_fuse as mount
