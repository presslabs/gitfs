import time

from gitfs.utils.decorators.while_not import while_not
from gitfs.worker.peasant import Peasant
from gitfs.events import pushing, fetching, read_only


class FetchWorker(Peasant):
    def run(self):
        while True:
            if self.stopped:
                break

            time.sleep(self.timeout)
            print "stats fetching"
            print pushing.is_set()
            self.fetch()

    @while_not(pushing)
    def fetch(self):
        fetching.set()
        try:
            print "fetch"
            behind = self.repository.fetch(self.upstream, self.branch)

            if behind:
                print "behind"
                self.merge_queue.add({"type": "merge"})
            if read_only.is_set():
                read_only.clear()
                print "no more read-only"
        except:
            read_only.set()
        fetching.clear()
