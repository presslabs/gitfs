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
from gitfs.log import log


class FetchWorker(Peasant):
    name = 'FetchWorker'

    def work(self):
        while True:
            fetch.wait(self.timeout)

            if shutting_down.is_set():
                log.info("Stop fetch worker")
                break

            self.fetch()

    def fetch(self):
        with remote_operation:
            fetch.clear()

            try:
                log.debug("Start fetching")
                self.repository.fetch(self.upstream, self.branch)
                fetch_successful.set()
                log.debug("Fetch done")
            except:
                fetch_successful.clear()
                log.exception("Fetch failed")
