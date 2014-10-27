# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pygit2

from gitfs.log import log
from .base import Merger


class AcceptMine(Merger):
    def _create_remote_copy(self, branch_name, upstream, new_branch):
        reference = "%s/%s" % (upstream, branch_name)
        remote = self.repository.lookup_branch(reference,
                                               pygit2.GIT_BRANCH_REMOTE)
        remote_commit = remote.get_object()

        local = self.repository.create_branch(new_branch, remote_commit)
        ref = self.repository.lookup_reference("refs/heads/%s" % new_branch)
        self.repository.checkout(ref, strategy=pygit2.GIT_CHECKOUT_FORCE)

        return local

    def _create_local_copy(self, branch_name, new_branch):
        old_branch = self.repository.lookup_branch(branch_name,
                                                   pygit2.GIT_BRANCH_LOCAL)
        return old_branch.rename(new_branch, True)

    def __call__(self, local_branch, remote_branch, upstream):
        log.debug("AcceptMine: Copy local branch to merging_local")
        local = self._create_local_copy(local_branch, "merging_local")

        log.debug("AcceptMine: Copy remote branch to merging_remote")
        remote = self._create_remote_copy(remote_branch, upstream,
                                          "merging_remote")

        log.debug("AcceptMine: Find diverge commis")
        diverge_commits = self.repository.find_diverge_commits(local, remote)

        reference = "refs/heads/%s" % "merging_remote"
        log.debug("AcceptMine: Checkout to %s", reference)
        self.repository.checkout(reference,
                                 strategy=pygit2.GIT_CHECKOUT_FORCE)

        # actual merging
        for commit in diverge_commits.first_commits:
            log.debug("AcceptMine: Merging %s", commit.hex)
            self.repository.merge(commit.hex)

            log.debug("AcceptMine: Solving conflicts")
            self.solve_conflicts(self.repository.index.conflicts)

            log.debug("AcceptMine: Commiting changes")
            ref = self.repository.lookup_reference(reference)
            message = "merging: %s" % commit.message
            parents = [ref.target, commit.id]
            new_commit = self.repository.commit(message, self.author,
                                                self.commiter, ref=reference,
                                                parents=parents)
            if new_commit is not None:
                log.debug("AcceptMine: We have a non-empty commit")
                self.repository.create_reference(reference,
                                                 new_commit, force=True)

            log.debug("AcceptMine: Checkout to %s", reference)
            self.repository.checkout(reference,
                                     strategy=pygit2.GIT_CHECKOUT_FORCE)

            log.debug("AcceptMine: Clean the state")
            self.repository.state_cleanup()

        log.debug("AcceptMine: Checkout to %s", local_branch)
        ref = self.repository.lookup_reference(reference)
        self.repository.create_reference("refs/heads/%s" % local_branch,
                                         ref.target,
                                         force=True)
        self.repository.checkout("refs/heads/%s" % local_branch,
                                 strategy=pygit2.GIT_CHECKOUT_FORCE)

        log.debug("AcceptMine: Delete merging_local")
        ref = self.repository.lookup_reference("refs/heads/merging_local")
        ref.delete()

        log.debug("AcceptMine: Delete merging_remote")
        ref = self.repository.lookup_reference("refs/heads/merging_remote")
        ref.delete()

    def solve_conflicts(self, conflicts):
        if conflicts:
            for common, theirs, ours in conflicts:
                if not ours and theirs:
                    log.debug("AcceptMine: if we deleted the file and they "
                              "didn't, remove the file")
                    self.repository.index.remove(theirs.path)
                elif ours and not theirs:
                    log.debug("AcceptMine: if they deleted the file and we "
                              "didn't, add the file")
                    self.repository.index.add(ours.path)
                else:
                    log.debug("AcceptMine: overwrite all file with our "
                              "content")
                    with open(self.repository._full_path(ours.path), "w") as f:
                        f.write(self.repository.get(ours.id).data)
                    self.repository.index.add(ours.path)
        else:
            log.info("AcceptMine: No conflicts to solve")
