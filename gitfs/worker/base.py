from threading import Thread


class Worker(Thread):
    def __init__(self, queue, repository, timeout=2, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)

        self.queue = queue
        self.repository = repository
        self.timeout = timeout

    def run(self):
        jobs = []
        while True:
            try:
                job = self.queue.get(timeout=self.timeout, block=True)
                jobs.append(job)
            except:
                if jobs:
                    self.execute(jobs)
                jobs = []

    def execute(self, jobs):
        raise NotImplemented("execute method should be implemented")
