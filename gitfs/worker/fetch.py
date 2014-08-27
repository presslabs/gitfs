import time
from threading import Thread


class FetchWorker(Thread):
    def __init__(self, upstream, branch, repository, merging, read_only,
                 timeout=5, *args, **kwargs):
        super(FetchWorker, self).__init__(*args, **kwargs)

        self.repository = repository
        self.upstream = upstream
        self.branch = branch
        self.merging = merging
        self.read_only = read_only
        self.timeout = timeout

    def run(self):
        while True:
            time.sleep(self.timeout)
            if not self.merging.is_set() and not self.read_only.is_set():
                try:
                    print "fetching"
                    self.repository.fetch(self.upstream, self.branch)
                except:
                    print "fetch failed...go read_only"
                    self.read_only.set()