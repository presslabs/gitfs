import time
from threading import Thread


class FetchWorker(Thread):
    def __init__(self, upstream, branch, repository, lock, merging,
                 *args, **kwargs):
        super(FetchWorker, self).__init__(*args, **kwargs)

        self.repository = repository
        self.upstream = upstream
        self.branch = branch
        self.merging = merging

    def run(self):
        while True:
            time.sleep(self.timeout)
            if not self.merging:
                self.repository.fetch(self.upstream, self.branch)
