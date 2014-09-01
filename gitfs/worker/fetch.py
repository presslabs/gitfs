import time
from threading import Thread

from gitfs.utils.decorators import retry


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

    @retry(1)
    def run(self):
        while True:
            time.sleep(self.timeout)
            if not self.merging.is_set():
                self.read_only.set()
                self.repository.fetch(self.upstream, self.branch)
