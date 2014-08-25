from gitfs.cache.commits import update_commits

from .base import Worker


class CommitWorker(Worker):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, push_queue, *args, **kwargs):
        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)
        self.push_queue = push_queue

        super(CommitWorker, self).__init__(*args, **kwargs)

    def execute(self, jobs):
        if len(jobs) == 1:
            message = jobs[0]['params']['message']
        else:
            updates = set([])
            for job in jobs:
                updates = updates | set(job['params']['add'])
                updates = updates | set(job['params']['remove'])

            message = "Update %s items" % len(updates)

        self.repository.commit(message, self.author, self.commiter)
        update_commits(self.repository)

        self.push_queue(message=message)
