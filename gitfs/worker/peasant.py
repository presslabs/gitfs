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


from threading import Thread

from gitfs.log import log


class Peasant(Thread):
    def __init__(self, *args, **kwargs):
        super(Peasant, self).__init__()

        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def run(self):
        try:
            self.work()
        except:
            log.exception("A worker is not feeling well")
