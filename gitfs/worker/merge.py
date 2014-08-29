from threading import Thread

import pygit2

from gitfs.utils.commits import CommitsList
from .decorators import while_not


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

        parent, merging_commits, local_commits = self.find_diverge_commits(merging_local, local_master)

        for commit in merging_commits:
            self.repository.merge(commit.hex)
            message = "Merging: %s" % commit.message
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

    def find_diverge_commits(self, first_branch, second_branch):
        sort = pygit2.GIT_SORT_TOPOLOGICAL

        first_iterator = self.repository.walk(first_branch.target, sort)
        second_iterator = self.repository.walk(second_branch.target, sort)

        first_commits = CommitsList()
        second_commits = CommitsList()

        try:
            first_commit = first_iterator.next()
        except:
            first_commit = None

        try:
            second_commit = second_iterator.next()
        except:
            second_commit = None

        while (first_commit not in second_commits and second_commit
               not in first_commits):

            if first_commit not in first_commits:
                first_commits.append(first_commit)
            if second_commit not in second_commits:
                second_commits.append(second_commit)

            try:
                first_commit = first_iterator.next()
            except:
                pass

            try:
                second_commit = second_iterator.next()
            except:
                pass

        if first_commit in second_commits:
            index = second_commits.index(first_commit)
            second_commits = second_commits[index:]
            common_parent = first_commit
        else:
            index = first_commits.index(second_commit)
            first_commits = first_commits[index:]
            common_parent = second_commit

        return common_parent, first_commits, second_commits

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
