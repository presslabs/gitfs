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
            #try:
            self.repository.fetch(self.upstream, self.branch)
            fetch_successful.set()
            #except:
            #    print "fetch failed"
            #    fetch_successful.clear()
