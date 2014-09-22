import time

from gitfs.utils.decorators.while_not import while_not
from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            if self.stopped:
                break

            time.sleep(self.timeout)
            self.fetch()

    @while_not("pushing")
    def fetch(self):
        self.fetching.set()
        try:
            print "fetch"
            behind = self.repository.fetch(self.upstream, self.branch)

            if behind:
                print "behind"
                self.merge_queue.add({"type": "merge"})
            if self.read_only.is_set():
                self.read_only.clear()
                print "no more read-only"
        except:
            self.read_only.set()
        self.fetching.clear()
