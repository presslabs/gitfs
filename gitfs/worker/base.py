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
