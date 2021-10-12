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


import sys
import argparse
import resource

from fuse import FUSE
from pygit2 import Keypair, UserPass, RemoteCallbacks

from gitfs import __version__
from gitfs.utils import Args
from gitfs.routes import prepare_routes
from gitfs.router import Router
from gitfs.worker import CommitQueue, SyncWorker, FetchWorker


def parse_args(parser):
    parser.add_argument("remote_url", help="repo to be cloned")
    parser.add_argument("mount_point", help="where the repo should be mount")
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "-o",
        help="other options: repo_path, user, "
        "group, branch, max_size, max_offset, "
        "fetch_timeout, merge_timeout, ssh_user",
    )

    return Args(parser)


def get_credentials(args):
    if args.password:
        credentials = UserPass(args.username, args.password)
    else:
        credentials = Keypair(args.ssh_user, args.ssh_key + ".pub", args.ssh_key, "")
    return RemoteCallbacks(credentials=credentials)


def prepare_components(args):
    commit_queue = CommitQueue()

    credentials = get_credentials(args)

    try:
        # setting router
        router = Router(
            remote_url=args.remote_url,
            mount_path=args.mount_point,
            current_path=args.current_path,
            history_path=args.history_path,
            repo_path=args.repo_path,
            branch=args.branch,
            user=args.user,
            group=args.group,
            max_size=args.max_size * 1024 * 1024,
            max_offset=args.max_size * 1024 * 1024,
            commit_queue=commit_queue,
            credentials=credentials,
            ignore_file=args.ignore_file,
            hard_ignore=args.hard_ignore,
        )
    except KeyError as error:
        sys.stderr.write(
            "Can't clone reference origin/%s from remote %s: %s\n"
            % (args.branch, args.remote_url, error)
        )
        raise error

    # register all the routes
    routes = prepare_routes(args)
    router.register(routes)

    # setup workers
    merge_worker = SyncWorker(
        args.commiter_name,
        args.commiter_email,
        args.commiter_name,
        args.commiter_email,
        commit_queue=commit_queue,
        repository=router.repo,
        upstream="origin",
        branch=args.branch,
        repo_path=router.repo_path,
        timeout=args.merge_timeout,
        credentials=credentials,
        min_idle_times=args.min_idle_times,
    )

    fetch_worker = FetchWorker(
        upstream="origin",
        branch=args.branch,
        repository=router.repo,
        timeout=args.fetch_timeout,
        credentials=credentials,
        idle_timeout=args.idle_fetch_timeout,
    )

    merge_worker.daemon = True
    fetch_worker.daemon = True

    router.workers = [merge_worker, fetch_worker]

    return merge_worker, fetch_worker, router


def start_fuse():
    parser = argparse.ArgumentParser(prog="GitFS")
    args = parse_args(parser)

    try:
        merge_worker, fetch_worker, router = prepare_components(args)
    except:
        return

    if args.max_open_files != -1:
        resource.setrlimit(
            resource.RLIMIT_NOFILE, (args.max_open_files, args.max_open_files)
        )

    # ready to mount it
    if sys.platform == "darwin":
        FUSE(
            router,
            args.mount_point,
            foreground=args.foreground,
            allow_root=args.allow_root,
            allow_other=args.allow_other,
            fsname=args.remote_url,
            subtype="gitfs",
        )
    else:
        FUSE(
            router,
            args.mount_point,
            foreground=args.foreground,
            nonempty=True,
            allow_root=args.allow_root,
            allow_other=args.allow_other,
            fsname=args.remote_url,
            subtype="gitfs",
        )


if __name__ == "__main__":
    start_fuse()
