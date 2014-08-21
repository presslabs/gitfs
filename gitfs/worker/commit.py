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

        if len(jobs) == 1:
            message = [jobs[0]['params']['message']]
        else:
            message = self._index_paths(add, 'add', "Updated %s items")
            message += self._index_paths(remove, 'remove',
                                         "\nRemoved %s items")

        self.repository.commit(message, self.author, self.commiter)

        self.push_queue(message=message)

    def _index_paths(self, paths, operation, message):
        if len(paths):
            for path in set(paths):
                if path.startswith("/"):
                    path = path[1:]
                getattr(self.repository.index, operation)(path)
            return message % len(set(paths))
        else:
            return ""
