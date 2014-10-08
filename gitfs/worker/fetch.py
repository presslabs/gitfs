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


from gitfs.worker.peasant import Peasant
from gitfs.events import (fetch, fetch_successful, shutting_down,
                          remote_operation)


class FetchWorker(Peasant):
    def run(self):
        while True:
            if shutting_down.is_set():
                break

            fetch.wait(self.timeout)
            self.fetch()

    def fetch(self):
        with remote_operation:
            print "acum fac fetch"
            fetch.clear()

            try:
                self.repository.fetch(self.upstream, self.branch)
                fetch_successful.set()
            except:
                print "fetch failed"
                fetch_successful.clear()
