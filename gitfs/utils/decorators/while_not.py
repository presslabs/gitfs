# Copyright 2014-2016 Presslabs SRL
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
try:
    from threading import _Event as Event  # Undocumented py2 class
except ImportError:
    from threading import Event
from functools import wraps


class while_not(object):
    def __init__(self, event, wait=0.2):
        self.event = event
        self.wait = wait

    def __call__(self, f):
        @wraps(f)
        def decorated(obj, *args, **kwargs):
            if not self.event:
                raise ValueError("Except that %s to not be "
                                 "None {}".format(obj.__class__.__name__))
            if not isinstance(self.event, Event):
                raise TypeError("{} should be of type threading."
                                "Event".format(self.event))

            while self.event.is_set():
                time.sleep(self.wait)

            return f(obj, *args, **kwargs)

        return decorated
