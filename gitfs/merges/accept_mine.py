import pygit2

from .base import BaseMerger


class AcceptMine(BaseMerger):
    def _create_local_copy(self, branch_name):
        old_branch = self.repository.lookup_branch(branch_name,
                                                   pygit2.GIT_BRANCH_LOCAL)
        return old_branch.rename("merging_local", True)

    def reload_branch(self, branch, upstream):
        remote = self.repository.lookup_branch("%s/%s" % (upstream, branch),
                                               pygit2.GIT_BRANCH_REMOTE)
        remote_commit = remote.get_object()

        local = self.repository.create_branch(branch, remote_commit)
        self.repository.create_reference("refs/heads/%s" % branch,
                                         local.target, force=True)

        ref = self.repository.lookup_reference("refs/heads/" % branch)
        self.repository.checkout(ref)

        return local

    def __call__(self, local_branch, remote_branch, upstream):
        # create local copy
        local_copy = self._create_local_copy(local_branch)

        # reload branch from remote
        local = self.reload_branch(local_branch, upstream)

        # get diverge commits
        diverge_commits = self.find_diverge_commits(local_copy, local)

        # acctual merging
        for commit in diverge_commits.first_commits:
            self.repository.merge(commit.hex)

            message = "Merging: %s" % commit.message
            commit = self.repository.commit(message, self.author,
                                            self.commiter)

            self.repository.create_reference("refs/heads/%s" % local_branch,
                                             commit,
                                             force=True)

            self.repository.checkout_head()
            self.repository.state_cleanup()

        self.repository.commits.update()
