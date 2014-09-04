import time

import pygit2
from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.fetch()

    def fetch(self):
        remote_commit = self.remote_commit

        try:
            self.repository.fetch(self.upstream, self.branch)

            if remote_commit.hex != self.remote_commit.hex:
                self.merge_queue.merge({"type": "merge"})

            self.read_only.clear()
        except:
            self.read_only.set()

    @property
    def remote_commit(self):
        ref = "%s/%s" % (self.upstream, self.branch)
        remote = self.repository.lookup_branch(ref, pygit2.GIT_BRANCH_REMOTE)
        return remote.get_object()
