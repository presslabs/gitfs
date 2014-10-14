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


from Queue import Queue

from gitfs.log import log


class BaseQueue(object):
    def __init__(self):
        self.queue = Queue()

    def commit(self, *args, **kwargs):
        raise NotImplemented()

    def get(self, *args, **kwargs):
        return self.queue.get(*args, **kwargs)


class CommitQueue(BaseQueue):

    def add(self, job):
        self.queue.put(job)

    def commit(self, add=None, message=None, remove=None):
        if message is None:
            raise ValueError("Message shoduld not be None")

        if add is None and remove is None:
            message = "You need to add or to remove some files from/to index"
            raise ValueError(message)

        self.queue.put({
            'type': 'commit',
            'params': {
                'add': self._to_list(add),
                'message': message,
                'remove': self._to_list(remove),
            }
        })
        log.debug("Got a new commit job on queue")

    def _to_list(self, variable):
        variable = variable or []

        if not isinstance(variable, list):
            variable = [variable]

        return variable
