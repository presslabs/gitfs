import time
from threading import Thread


class PullWorker(Thread):
    def __init__(self, upstream, branch, repository, lock, timeout=4,
                 *args, **kwargs):
        super(PullWorker, self).__init__(*args, **kwargs)

        self.repository = repository
        self.lock = lock
        self.upstream = upstream
        self.branch = branch
        self.timeout = timeout

    def run(self):
        while True:
            time.sleep(self.timeout)
            with self.lock:
                self.repository.pull(self.upstream, self.branch)
