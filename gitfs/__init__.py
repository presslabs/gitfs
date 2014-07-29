from fuse import FuseOSError, ENOTSUP


FuseMethodNotImplemented = FuseOSError(ENOTSUP)

