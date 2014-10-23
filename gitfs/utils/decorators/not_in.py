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


import errno
import inspect
from functools import wraps

from fuse import FuseOSError


class not_in(object):
    def __init__(self, look_at, check=None):
        self.look_at = look_at
        self.check = check

    def __call__(self, f):
        @wraps(f)
        def decorated(their_self, *args, **kwargs):
            # TODO: check for look_at in self first
            if isinstance(self.look_at, basestring):
                self.look_at = getattr(their_self, self.look_at)

            self.check_args(f, args)
            result = f(their_self, *args, **kwargs)

            return result

        return decorated

    def check_args(self, f, methods_args):
        to_check = []

        args = inspect.getargspec(f)
        for arg in self.check:
            if arg in args[0]:
                to_check.append(args[0].index(arg))

        for index in to_check:
            arg = methods_args[index - 1]

            if self.look_at.cache.get(arg, False):
                raise FuseOSError(errno.EACCES)

            if self.look_at.check_key(arg):
                self.look_at.cache[arg] = True
                raise FuseOSError(errno.ENOENT)

            self.look_at.cache[arg] = False
