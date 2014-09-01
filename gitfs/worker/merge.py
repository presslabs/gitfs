from threading import Thread

from gitfs.merges import AcceptMine

from .decorators import while_not


class MergeWorker(Thread):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, merging, somebody_is_writing, read_only,
                 merge_queue, repository, upstream, branch, repo_path,
                 strategy=None, timeout=5, *args, **kwargs):
        super(MergeWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        self.merge_queue = merge_queue
        self.repository = repository
        self.upstream = upstream
        self.branch = branch

        self.timeout = timeout
        self.merging = merging
        self.read_only = read_only
        self.somebody_is_writing = somebody_is_writing

        default = AcceptMine(repository, author=self.author,
                             commiter=self.commiter, repo_path=repo_path)
        self.strategy = default

        super(MergeWorker, self).__init__(*args, **kwargs)

    def run(self):
        jobs = []
        while True:
            try:
                job = self.merge_queue.get(timeout=self.timeout, block=True)
                jobs.append(job)
            except:
                if jobs:
                    self.commit(jobs)
                    self.fetch()
                    self.merge()
                    self.push()
                jobs = []

    @while_not("read_only")
    def fetch(self):
        try:
            self.repository.fetch(self.upstream, self.branch)
        except:
            self.read_only.set()

    @while_not("read_only")
    @while_not("somebody_is_writing")
    def merge(self):
        self.merging.set()

        self.strategy(self.branch, self.branch, self.upstream)

        # update commits cache
        self.repository.commits.update()

        self.merging.clear()

    def push(self):
        try:
            self.repository.push(self.upstream, self.branch)
            self.read_only.clear()
        except:
            self.read_only.set()

    def commit(self, jobs):
        if len(jobs) == 1:
            message = jobs[0]['params']['message']
        else:
            updates = set([])
            for job in jobs:
                updates = updates | set(job['params']['add'])
                updates = updates | set(job['params']['remove'])

            message = "Update %s items" % len(updates)

        self.repository.commit(message, self.author, self.commiter)
        self.repository.commits.update()
