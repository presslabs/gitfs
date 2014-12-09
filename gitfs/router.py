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


import re
import os
import time
import shutil
import inspect

from pwd import getpwnam
from grp import getgrnam

from errno import ENOSYS

from fuse import FUSE, FuseOSError

from gitfs.repository import Repository
from gitfs.cache import CachedIgnore, lru_cache
from gitfs.events import shutting_down, fetch
from gitfs.log import log


class Router(object):
    def __init__(self, remote_url, repo_path, mount_path, credentials,
                 branch=None, user="root", group="root", **kwargs):
        """
        Clone repo from a remote into repo_path/<repo_name> and checkout to
        a specific branch.

        :param str remote_url: URL of the repository to clone
        :param str repo_path: Where are all the repos are cloned
        :param str branch: Branch to checkout after the
            clone. The default is to use the remote's default branch.

        """

        self.remote_url = remote_url
        self.repo_path = repo_path
        self.mount_path = mount_path
        self.branch = branch

        self.routes = []

        log.info('Cloning into %s' % self.repo_path)

        self.repo = Repository.clone(self.remote_url, self.repo_path,
                                     self.branch, credentials)
        log.info('Done cloning')

        self.repo.credentials = credentials

        submodules = os.path.join(self.repo_path, '.gitmodules')
        ignore = os.path.join(self.repo_path, '.gitignore')
        self.repo.ignore = CachedIgnore(submodules=submodules,
                                        ignore=ignore,
                                        exclude=kwargs['ignore_file'] or None,
                                        hard_ignore=kwargs['hard_ignore'])

        self.uid = getpwnam(user).pw_uid
        self.gid = getgrnam(group).gr_gid

        self.commit_queue = kwargs['commit_queue']
        self.mount_time = int(time.time())

        self.max_size = kwargs['max_size']
        self.max_offset = kwargs['max_offset']

        self.repo.commits.update()

        self.workers = []

    def init(self, path):
        for worker in self.workers:
            worker.start()

        log.debug('Done init')

    def destroy(self, path):
        log.debug('Stopping workers')
        shutting_down.set()
        fetch.set()

        for worker in self.workers:
            worker.join()
        log.debug('Workers stopped')

        shutil.rmtree(self.repo_path)
        log.info('Successfully umounted %s', self.mount_path)

    def __call__(self, operation, *args):
        """
        Magic method which calls a specific method from a view.

        In Fuse API, almost each method receives a path argument. Based on that
        path we can route each call to a specific view. For example, if a
        method which has a path argument like `/current/dir1/dir2/file1` is
        called, we need to get the certain view that will know how to handle
        this path, instantiate it and then call our method on the newly created
        object.

        :param str operation: Method name to be called
        :param args: tuple containing the arguments to be transmitted to
            the method
        :rtype: function
        """

        if operation in ['destroy', 'init']:
            view = self
        else:
            path = args[0]
            view, relative_path = self.get_view(path)
            args = (relative_path,) + args[1:]

        log.debug('Call %s %s with %r' % (operation,
                                          view.__class__.__name__,
                                          args))

        if not hasattr(view, operation):
            log.debug('No attribute %s on %s' % (operation,
                      view.__class__.__name__))
            raise FuseOSError(ENOSYS)

        try:
            return getattr(view, operation)(*args)
        except FuseOSError as e:
            raise e
        except Exception as exception:
            log.exception("A system call failed")
            raise exception

    def register(self, routes):
        for regex, view in routes:
            log.debug('Registering %s for %s', view, regex)
            self.routes.append({
                'regex': regex,
                'view': view
            })

    def get_view(self, path):
        """
        Try to map a given path to it's specific view.

        If a match is found, a view object is created with the right regex
        groups(named or unnamed).

        :param str path: path to be matched
        :rtype: view object, relative path
        """

        for route in self.routes:
            result = re.search(route['regex'], path)
            if result is None:
                continue

            groups = result.groups()
            relative_path = re.sub(route['regex'], '', path)
            relative_path = '/' if not relative_path else relative_path

            cache_key = result.group(0)
            log.debug("Router: Cache key for %s: %s", path, cache_key)

            view = lru_cache.get_if_exists(cache_key)
            if view is not None:
                log.debug("Router: Serving %s from cache", path)
                return view, relative_path

            kwargs = result.groupdict()

            # TODO: move all this to a nice config variable
            kwargs['repo'] = self.repo
            kwargs['ignore'] = self.repo.ignore
            kwargs['repo_path'] = self.repo_path
            kwargs['mount_path'] = self.mount_path
            kwargs['regex'] = route['regex']
            kwargs['relative_path'] = relative_path
            kwargs['uid'] = self.uid
            kwargs['gid'] = self.gid
            kwargs['branch'] = self.branch
            kwargs['mount_time'] = self.mount_time
            kwargs['queue'] = self.commit_queue
            kwargs['max_size'] = self.max_size
            kwargs['max_offset'] = self.max_offset

            args = set(groups) - set(kwargs.values())
            view = route['view'](*args, **kwargs)

            lru_cache[cache_key] = view
            log.debug("Router: Added %s to cache", path)

            return view, relative_path

        raise ValueError("View not found!")

    def __getattr__(self, attr_name):
        """
        It will only be called by the `__init__` method from `fuse.FUSE` to
        establish which operations will be allowed after mounting the
        filesystem.
        """

        methods = inspect.getmembers(FUSE, predicate=inspect.ismethod)
        fuse_allowed_methods = set([elem[0] for elem in methods])

        return attr_name in fuse_allowed_methods - set(['bmap', 'lock'])
