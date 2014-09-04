from gitfs.utils.decorators import retry

from gitfs.merges import AcceptMine
from gitfs.utils.decorators import while_not
from gitfs.worker.fetch import FetchWorker


class MergeWorker(FetchWorker):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, strategy=None, *args, **kwargs):
        super(MergeWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        strategy = strategy or AcceptMine(self.repository, author=self.author,
                                          commiter=self.commiter,
                                          repo_path=self.repo_path)
        self.strategy = strategy

    def run(self):
        commits = []
        merges = []

        while True:
            try:
                job = self.merge_queue.get(timeout=self.timeout, block=True)

                # we have two types of jobs: [commit, merge]
                if job['type'] == 'commit':
                    commits.append(job)
                elif job['type'] == 'merge':
                    merges.append(job)
            except:
                commits, merges = self.on_idle(commits, merges)

    def on_idle(self, commits, merges):
        """
        On idle, we have 4 cases:
        1. We have to commit and also need to merge some commits from remote.
        In this case, we commit and announce ourself for merging
        2. We are behind from remote, so we announce for merging
        3. We only need to commit
        4. We announced for merging and nobody is writing in this momement.
        In this case we are safe to merge and push.
        """

        if commits and merges:
            self.commit(commits)
            self.want_to_merge.set()
            commits = []
            merges = []
        elif merges:
            self.want_to_merge.set()
            merges = []
        elif commits:
            self.commit(commits)
            self.want_to_merge.set()
            commits = []
        elif (self.want_to_merge.is_set() and
              not self.somebody_is_writing.is_set()):
            self.merge()
            self.want_to_merge.clear()
            self.push()

        return commits, merges

    @while_not("read_only")
    def merge(self):
        self.strategy(self.branch, self.branch, self.upstream)
        self.repository.commits.update()

    @retry(3)
    def push(self):
        """
        Try to push. The push can fail in two cases:
        1. The remote is done, so we need to retry.
        2. We are behind, so we need to fetch + merge and then try again
        """

        self.read_only.set()

        try:
            self.repository.push(self.upstream, self.branch)
            self.read_only.clear()
        except:
            pass

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
        self.repository.checkout_head()
