import os

import pygit2

from .base import Merger


class AcceptMine(Merger):
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

        ref = self.repository.lookup_reference("refs/heads/%s" % branch)
        self.repository.checkout(ref)

        return local

    def __call__(self, local_branch, remote_branch, upstream):
        # create local copy
        local_copy = self._create_local_copy(local_branch)

        # reload branch from remote
        local = self.reload_branch(local_branch, upstream)

        # get diverge commits
        diverge_commits = self.find_diverge_commits(local_copy, local)

        # actual merging
        for commit in diverge_commits.first_commits:
            print commit.message
            self.repository.merge(commit.hex)

            # resolve conflicts
            self.solve_conflicts(self.repository.index.conflicts)

            message = "%s " % commit.message
            commit = self.repository.commit(message, self.author,
                                            self.commiter,
                                            "refs/heads/%s" % local_branch)

            self.repository.create_reference("refs/heads/%s" % local_branch,
                                             commit,
                                             force=True)

            self.repository.checkout_head()
            self.repository.state_cleanup()

    def solve_conflicts(self, conflicts):
        if conflicts:
            for common, theirs, ours in conflicts:
                # if we deleted the file and they didn't, remove the file
                if not ours and theirs:
                    self.repository.index.remove(theirs.path)
                # if they deleted the file and we didn't, add the file
                elif ours and not theirs:
                    self.repository.index.add(ours.path)
                # otherwise, overwrite all file with our content
                else:
                    with open(self._full_path(ours.path), "w") as f:
                        f.write(self.repository.get(ours.id).data)
                    self.repository.index.add(ours.path)

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.repo_path, partial)

        return path
