import pygit2

from gitfs.merges import AcceptMine
from gitfs.worker.fetch import FetchWorker

from gitfs.utils.decorators.retry import retry
from gitfs.utils.decorators.while_not import while_not


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
            if self.stopped:
                break

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

    def merge(self):
        self.strategy(self.branch, self.branch, self.upstream)
        self.repository.commits.update()
        self.repository.ignore.update()

    @while_not("fetching")
    def push(self):
        """
        Try to push. The push can fail in two cases:
        1. The remote is down, so we need to retry.
        2. We are behind, so we need to fetch + merge and then try again
        """

        self.pushing.set()
        self.read_only.set()

        try:
            print "try to push"
            self.repository.push(self.upstream, self.branch)
            print "push done"
            self.read_only.clear()
        except:
            print "push failed"
            self.fetch()
        self.pushing.clear()

    @retry(each=3)
    def fetch(self):
        print "try to fetch"
        behind = self.repository.fetch(self.upstream, self.branch)
        if behind:
            print "behind"
            self.merge_queue.add({'type': 'merge'})
        else:
            print "ok...pushing"
            self.push()

    def commit(self, jobs):
        if len(jobs) == 1:
            message = jobs[0]['params']['message']
        else:
            updates = set([])
            for job in jobs:
                updates = updates | set(job['params']['add'])
                updates = updates | set(job['params']['remove'])

            message = "Update %s items" % len(updates)

        print "commiting %s" % message
        self.repository.commit(message, self.author, self.commiter)
        self.repository.commits.update()
        self.repository.checkout_head(strategy=pygit2.GIT_CHECKOUT_FORCE)
