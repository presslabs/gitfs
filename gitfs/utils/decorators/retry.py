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


import time
from functools import wraps


class retry(object):
    def __init__(self, each=3, times=True):
        self.each = each
        self.times = times

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            while self.times:
                try:
                    return f(*args, **kwargs)
                except:
                    time.sleep(self.each)

                if (isinstance(self.times, int) and not
                   isinstance(self.times, bool)):
                    self.times -= 1

            return f(*args, **kwargs)

        return decorated
