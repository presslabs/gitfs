# Copyright 2014-2016 Presslabs SRL
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
import random

import time
from six.moves.queue import Empty

import pygit2

from gitfs.worker.peasant import Peasant
from gitfs.merges import AcceptMine

from gitfs.events import (fetch, syncing, sync_done, writers, shutting_down,
                          remote_operation, push_successful, idle)
from gitfs.log import log


class SyncWorker(Peasant):
    name = 'SyncWorker'

    def __init__(self, author_name, author_email, commiter_name,
                 commiter_email, strategy=None, *args, **kwargs):
        super(SyncWorker, self).__init__(*args, **kwargs)

        self.author = (author_name, author_email)
        self.commiter = (commiter_name, commiter_email)

        strategy = strategy or AcceptMine(self.repository, author=self.author,
                                          commiter=self.commiter,
                                          repo_path=self.repo_path)
        self.strategy = strategy
        self.commits = []

    def work(self):
        idle_times = 0
        while True:
            if shutting_down.is_set():
                log.info("Stop sync worker")
                break

            try:
                job = self.commit_queue.get(timeout=self.timeout, block=True)
                if job['type'] == 'commit':
                    self.commits.append(job)
                log.debug("Got a commit job")

                idle_times = 0
                idle.clear()
            except Empty:
                log.debug("Nothing to do right now, going idle")

                if idle_times > self.min_idle_times:
                    idle.set()

                idle_times += 1
                self.on_idle()

    def on_idle(self):
        """
        On idle, we have 4 cases:
        1. We have to commit and also need to merge some commits from remote.
        In this case, we commit and announce ourself for merging
        2. We are behind from remote, so we announce for merging
        3. We only need to commit
        4. We announced for merging and nobody is writing in this momement.
        In this case we are safe to merge and push.
        """

        if not syncing.is_set():
            log.debug("Set syncing event (%d pending writes)", writers.value)
            syncing.set()
        else:
            log.debug("Idling (%d pending writes)", writers.value)

        if writers.value == 0:
            if self.commits:
                log.info("Get some commits")
                self.commit(self.commits)
                self.commits = []

            count = 0
            log.debug("Start syncing, first attempt.")
            while not self.sync() and count < 5:
                fuzz = random.randint(0, 1000) / 1000
                wait = 2 ** count + fuzz

                log.debug("Failed to sync. Going to sleep for %d seconds", wait)
                time.sleep(wait)

                count += 1
                log.debug("Retry-ing to sync with remote. Attempt #%d", count)

            if count >= 5:
                log.debug("Didn't manage to sync, I need some help")


    def merge(self):
        log.debug("Start merging")
        self.strategy(self.branch, self.branch, self.upstream)

        log.debug("Update commits cache")
        self.repository.commits.update()

        log.debug("Update ignore list")
        self.repository.ignore.update()

    def sync(self):
        log.debug("Check if I'm ahead")
        need_to_push = self.repository.ahead(self.upstream, self.branch)
        sync_done.clear()

        if self.repository.behind:
            log.debug("I'm behind so I start merging")
            try:
                log.debug("Start fetching")
                self.repository.fetch(self.upstream, self.branch,
                                      self.credentials)
                log.debug("Done fetching")
                log.debug("Start merging")
                self.merge()
                log.debug("Merge done with success, ready to push")
                need_to_push = True
            except:
                log.exception("Merge failed")
                return False

        if need_to_push:
            try:
                with remote_operation:
                    log.debug("Start pushing")
                    self.repository.push(self.upstream, self.branch,
                                         self.credentials)
                    self.repository.behind = False
                    log.info("Push done")
                log.debug("Clear syncing")
                syncing.clear()
                log.debug("Set sync_done")
                sync_done.set()
                log.debug("Set push_successful")
                push_successful.set()
            except:
                push_successful.clear()
                fetch.set()
                log.exception("Push failed")
                return False
        else:
            log.debug("Sync done, clearing")
            sync_done.set()
            syncing.clear()

        return True

    def commit(self, jobs):
        if len(jobs) == 1:
            message = jobs[0]['params']['message']
        else:
            updates = set([])
            for job in jobs:
                updates = updates | set(job['params']['add'])
                updates = updates | set(job['params']['remove'])

            message = "Update {} items".format(len(updates))

        old_head = self.repository.head.target
        new_commit = self.repository.commit(message, self.author,
                                            self.commiter)

        if new_commit:
            log.debug("Commit %s with %s as author and %s as commiter",
                      message, self.author, self.commiter)
            self.repository.commits.update()
            log.debug("Update commits cache")
        else:
            self.repository.create_reference("refs/heads/%s" % self.branch,
                                             old_head, force=True)
        self.repository.checkout_head(strategy=pygit2.GIT_CHECKOUT_FORCE)
        log.debug("Checkout to HEAD")
