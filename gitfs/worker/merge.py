from threading import Thread


class MergeWorker(Thread):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, merging, merge_queue, repository,
                 upstream, branch, timeout=5, *args, **kwargs):
        super(MergeWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        self.merge_queue = merge_queue
        self.repository = repository
        self.upstream = upstream
        self.branch = branch

        self.timeout = timeout
        self.merging = merging

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
                    self.merge()
                    self.push()
                jobs = []

    def merge(self):
        # TODO: implement merging logic here
        self.merging = True

    def push(self):
        # TODO: we need to block the fs if this will fail
        self.repository.push(self.upstream, self.branch)

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
