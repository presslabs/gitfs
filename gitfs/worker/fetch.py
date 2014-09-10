import time

from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.fetch()

    def fetch(self):

        try:
            print "fetch"
            behind = self.repository.fetch(self.upstream, self.branch)

            if behind:
                print "behind"
                self.merge_queue.add({"type": "merge"})
            if self.read_only.is_set():
                self.read_only.clear()
                print "no more read-only"
        except Exception as e:
            print e
            self.read_only.set()
