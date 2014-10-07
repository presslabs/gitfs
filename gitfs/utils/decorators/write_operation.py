from errno import EROFS
from functools import wraps

from fuse import FuseOSError

from gitfs.events import (sync_done, syncing, writers, push_successful,
                          fetch_successful)


def write_operation(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not fetch_successful.is_set() or not push_successful.is_set():
            raise FuseOSError(EROFS)

        global writers
        writers += 1

        if syncing.is_set():
            sync_done.wait()

        try:
            result = f(*args, **kwargs)
        finally:
            writers -= 1

        return result
    return decorated
