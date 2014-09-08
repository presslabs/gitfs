import time

from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.fetch()

    def fetch(self):
        print "no more read-only"
        self.read_only.clear()

        try:
            print "fetch"
            behind = self.repository.fetch(self.upstream, self.branch)

            if behind:
                print "behind"
                self.merge_queue.add({"type": "merge"})
        except:
            self.read_only.set()
