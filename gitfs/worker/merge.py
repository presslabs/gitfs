from threading import Thread
from .decorators import while_not

import pygit2


class MergeWorker(Thread):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, merging, read_only, merge_queue, repository,
                 upstream, branch, timeout=5, *args, **kwargs):
        super(MergeWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        self.merge_queue = merge_queue
        self.repository = repository
        self.upstream = upstream
        self.branch = branch

        self.timeout = timeout
        self.merging = merging
        self.read_only = read_only

        super(MergeWorker, self).__init__(*args, **kwargs)

    def run(self):
        jobs = []
        while True:
            try:
                job = self.merge_queue.get(timeout=self.timeout, block=True)
                jobs.append(job)
            except:
                if jobs:
                    self.commit(jobs)
                    self.merge()
                    self.push()
                jobs = []

    @while_not("read_only")
    def merge(self):
        self.merging.set()

        # rename the master branch
        old_master = self.repository.lookup_branch(self.branch,
                                                   pygit2.GIT_BRANCH_LOCAL)
        merging_local = old_master.rename("merging_local", True)

        remote_master = "%s/%s" % (self.upstream, self.branch)
        remote_master = self.repository.lookup_branch(remote_master,
                                                      pygit2.GIT_BRANCH_REMOTE)

        remote_commit = remote_master.get_object()

        local_master = self.repository.create_branch("master", remote_commit)

        self.repository.create_reference("refs/heads/master",
                                         local_master.target, force=True)

        ref = self.repository.lookup_reference("refs/heads/master")
        self.repository.checkout(ref)

        for merging_commit, local_commit in self.yield_commits(merging_local,
                                                               local_master):
            if merging_commit is None:
                continue

            if merging_commit.hex != local_commit.hex:

                self.repository.merge(merging_commit.hex)
                message = "Merging: %s" % merging_commit.message
                commit = self.repository.commit(message,
                                                self.author,
                                                self.commiter)
                self.repository.commits.update()
                self.repository.create_reference("refs/heads/master", commit,
                                                 force=True)
                self.repository.checkout_head()
                self.repository.state_cleanup()

        print "done merging"

        self.merging.clear()

    def get_commits(self, merging_branch, remote_branch):
        commits = []
        for merging_commit, remote_commit in self.yield_commits(merging_branch,
                                                                remote_branch):
            if merging_commit != remote_commit:
                commits.append((merging_commit, remote_commit))
        return commits

    def yield_commits(self, first_branch, second_branch):
        first_iterator = self.repository.walk(first_branch.target,
                                              pygit2.GIT_SORT_TIME)
        second_iterator = self.repository.walk(second_branch.target,
                                               pygit2.GIT_SORT_TIME)

        for first_commit in first_iterator:
            try:
                second_commit = second_iterator.next()
            except:
                second_commit = None
            yield (first_commit, second_commit)

        while second_commit is not None:
            try:
                second_commit = second_iterator.next()
            except:
                second_commit = None
            yield (None, second_commit)

    @while_not("read_only")
    def push(self):
        try:
            print "pushing"
            self.repository.push(self.upstream, self.branch)
            print "pushed"
        except:
            print "pushed failed, go read_only"
            self.read_only.set()

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
