import time
from threading import Thread


class FetchWorker(Thread):
    def __init__(self, upstream, branch, repository, merging, timeout=5,
                 *args, **kwargs):
        super(FetchWorker, self).__init__(*args, **kwargs)

        self.repository = repository
        self.upstream = upstream
        self.branch = branch
        self.merging = merging
        self.timeout = timeout

    def run(self):
        while True:
            time.sleep(self.timeout)
            if not self.merging.is_set():
                self.repository.fetch(self.upstream, self.branch)
