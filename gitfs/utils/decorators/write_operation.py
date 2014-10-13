# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from errno import EROFS
from functools import wraps

from fuse import FuseOSError

from gitfs.events import (sync_done, syncing, writers, push_successful,
                          fetch_successful)
from gitfs.log import log


def write_operation(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not fetch_successful.is_set() or not push_successful.is_set():
            raise FuseOSError(EROFS)

        global writers
        writers += 1

        if syncing.is_set():
            log.debug("WriteOperation: Wait until syncing is done")
            sync_done.wait()

        try:
            result = f(*args, **kwargs)
        finally:
            writers -= 1

        return result
    return decorated
