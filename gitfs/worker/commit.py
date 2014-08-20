from .base import Worker


class CommitWorker(Worker):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, push_queue, *args, **kwargs):
        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)
        self.push_queue = push_queue

        super(CommitWorker, self).__init__(*args, **kwargs)

    def execute(self, jobs):
        add = []
        remove = []
        message = []

        for job in jobs:
            add += job['params']['add']
            remove += job['params']['remove']

        if len(add):
            for path in set(add):
                if path.startswith("/"):
                    path = path[1:]

                self.repository.index.add(path)
            message.append("Updated %s items" % len(set(add)))

        if len(remove):
            for path in set(remove):
                if path.startswith("/"):
                    path = path[1:]

                self.repository.index.remove(path)
            message.append("Removed %s items" % len(set(remove)))

        if len(jobs) == 1:
            message = [jobs[0]['params']['message']]

        message = "\n".join(message)
        self.repository.commit(message, self.author, self.commiter)

        self.push_queue(message=message)
