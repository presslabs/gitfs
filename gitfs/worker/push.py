from .base import Worker


class PushWorker(Worker):
    def __init__(self, upstream, branch, *args, **kwargs):
        super(PushWorker, self).__init__(args, kwargs)
        self.upstream = upstream
        self.branch = branch

    def execute(self, jobs):
        self.repository.push(self.upstream, self.branch)
