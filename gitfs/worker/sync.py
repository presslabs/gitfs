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

from Queue import Empty

import pygit2

from gitfs.worker.peasant import Peasant
from gitfs.merges import AcceptMine

from gitfs.events import (fetch, syncing, sync_done, writers, shutting_down,
                          remote_operation, push_successful)
from gitfs.log import log


class SyncWorker(Peasant):
    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, strategy=None, *args, **kwargs):
        super(SyncWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        strategy = strategy or AcceptMine(self.repository, author=self.author,
                                          commiter=self.commiter,
                                          repo_path=self.repo_path)
        self.strategy = strategy

    def run(self):
        commits = []

        while True:
            if shutting_down.is_set():
                break

            try:
                job = self.commit_queue.get(timeout=self.timeout, block=True)
                if job['type'] == 'commit':
                    commits.append(job)
                log.debug("SyncWorker: Got a commit job")
            except Empty:
                log.debug("SyncWorker: Nothing to do right now, going idle")
                commits = self.on_idle(commits)

    def on_idle(self, commits):
        """
        On idle, we have 4 cases:
        1. We have to commit and also need to merge some commits from remote.
        In this case, we commit and announce ourself for merging
        2. We are behind from remote, so we announce for merging
        3. We only need to commit
        4. We announced for merging and nobody is writing in this momement.
        In this case we are safe to merge and push.
        """

        if commits:
            log.debug("SyncWorker: Get some commits")
            self.commit(commits)
            commits = []
            log.debug("SyncWorker: Set syncing event")
            syncing.set()

        if writers == 0:
            self.sync()

        return commits

    def merge(self):
        log.debug("SyncWorker: Start merging")
        self.strategy(self.branch, self.branch, self.upstream)

        log.debug("SyncWorker: Update commits cache")
        self.repository.commits.update()

        log.debug("SyncWorker: Update ignore list")
        self.repository.ignore.update()

    def sync(self):
        need_to_push = self.repository.ahead(self.upstream, self.branch)
        sync_done.clear()

        if self.repository.behind:
            log.debug("SyncWorker: I'm behind so I start merging")
            self.merge()
            need_to_push = True

        if need_to_push:
            try:
                with remote_operation:
                    log.info("SyncWorker: Start pushing")
                    self.repository.push(self.upstream, self.branch)
                    self.repository.behind = False
                    log.info("SyncWorker: Push done")
                log.debug("SyncWorker: Clear syncing")
                syncing.clear()
                log.debug("SyncWorker: Set sync_done")
                sync_done.set()
                log.debug("SyncWorker: Set push_successful")
                push_successful.set()
            except:
                log.info("SyncWorker: Push failed")
                push_successful.clear()
                fetch.set()

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
        log.info("SyncWorker: Commit %s with %s as author and %s as commiter",
                 message, self.author, self.commiter)
        self.repository.commits.update()
        log.debug("Update commits cache")
        self.repository.checkout_head(strategy=pygit2.GIT_CHECKOUT_FORCE)
        log.debug("Checkout to HEAD")
