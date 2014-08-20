from threading import Thread


class Worker(Thread):
    def __init__(self, queue, repository, timeout=2):
        self.queue = queue
        self.repository = repository
        self.timeout = timeout

    def run(self):
        while True:
            jobs = []
            try:
                job = self.queue.get(timeout=self.timeout, block=True)
                jobs.append(job)
            except:
                if jobs:
                    self.execute(jobs)

    def execute(self, jobs):
        raise NotImplemented("execute method should be implemented")


class CommitWorker(Worker):
    def __init__(self, author, commiter, *args, **kwargs):
        self.author = author
        self.commiter = commiter
        super(Worker, self).__init__(*args, **kwargs)

    def execute(self, jobs):
        message = ""

        for job in jobs:
            pass

        self.repository(message, self.author, self.commiter)
