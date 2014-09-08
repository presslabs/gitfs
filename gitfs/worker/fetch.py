import time

from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.fetch()

    def fetch(self):
        try:
            behind = self.repository.fetch(self.upstream, self.branch)

            if behind:
                self.merge_queue.add({"type": "merge"})

            self.read_only.clear()
        except:
            self.read_only.set()
