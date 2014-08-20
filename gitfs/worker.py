import Queue
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
            except Queue.Empty:
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
        add = []
        remove = []
        message = []

        for job in jobs:
            add += job['add']
            remove += job['remove']

        if len(add):
            for path in set(add):
                self.repository.index.add(path)
            message.append("Updated %s items" % len(set(add)))

        if len(remove):
            for path in set(remove):
                self.repository.index.remove(path)
            message.append("Removed %s items" % len(set(remove)))

        if len(jobs) == 1:
            message = [jobs[0]['message']]

        message = "\n".join(message)
        self.repository.commit(message, self.author, self.commiter)
