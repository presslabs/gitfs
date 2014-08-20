from .base import Worker


class CommitWorker(Worker):
    def __init__(self, push_queue, author_name, author_email, commiter_name,
                 commiter_email, *args, **kwargs):
        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)
        self.push_queue = push_queue

        super(Worker, self).__init__(*args, **kwargs)

    def execute(self, jobs):
        add = []
        remove = []
        message = []

        for job in jobs['params']:
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

        self.push_queue(message=message)
