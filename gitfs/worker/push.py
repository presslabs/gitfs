from .base import Worker


class PushWorker(Worker):
    def __init__(self, upstream, branch, lock, *args, **kwargs):
        self.upstream = upstream
        self.branch = branch
        self.lock = lock
        super(PushWorker, self).__init__(*args, **kwargs)

    def execute(self, jobs):
        with self.lock:
            print "push"
            self.repository.push(self.upstream, self.branch)
