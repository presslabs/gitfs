import time

from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.fetch()

    def fetch(self):
        remote_commit = self.repository.remote_head(self.upstream, self.branch)

        try:
            self.repository.fetch(self.upstream, self.branch)

            new_remote_commit = self.repository.remote_head(self.upstream,
                                                            self.branch)
            if remote_commit.hex != new_remote_commit.hex:
                self.merge_queue.add({"type": "merge"})

            self.read_only.clear()
        except:
            self.read_only.set()
