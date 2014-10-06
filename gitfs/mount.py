import argparse
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler, SysLogHandler
import tempfile
import threading
import sys

from fuse import FUSE
from gitfs.log import log

from gitfs.utils import Args
from gitfs.routes import routes
from gitfs.router import Router
from gitfs.worker import MergeQueue, MergeWorker, FetchWorker


def parse_args(parser):
    parser.add_argument('remote_url', help='repo to be cloned')
    parser.add_argument('mount_point', help='where the repo should be mount')
    parser.add_argument('-o', help='other options: repos_path, user, '
                                   'group, branch, max_size, max_offset, '
                                   'fetch_timeout, merge_timeout')
    return Args(parser)


def prepare_components(args):
    # initialize merge queue
    merge_queue = MergeQueue()
    want_to_merge = threading.Event()
    read_only = threading.Event()
    somebody_is_writing = threading.Event()
    merging = threading.Event()
    fetching = threading.Event()
    pushing = threading.Event()

    # setting router
    router = Router(remote_url=args.remote_url,
                    mount_path=args.mount_point,
                    repos_path=args.repos_path,
                    branch=args.branch,
                    user=args.user,
                    group=args.group,
                    max_size=args.max_size * 1024 * 1024,
                    max_offset=args.max_size * 1024 * 1024,
                    merge_queue=merge_queue,
                    want_to_merge=want_to_merge,
                    somebody_is_writing=somebody_is_writing,
                    read_only=read_only)

    # register all the routes
    router.register(routes)

    # setup workers
    merge_worker = MergeWorker(args.commiter_name, args.commiter_email,
                               args.commiter_name, args.commiter_email,
                               want_to_merge=want_to_merge,
                               somebody_is_writing=somebody_is_writing,
                               read_only=read_only,
                               merge_queue=merge_queue,
                               merging=merging,
                               repository=router.repo,
                               upstream="origin",
                               branch=args.branch,
                               repo_path=router.repo_path,
                               timeout=args.merge_timeout,
                               fetching=fetching,
                               pushing=pushing)

    fetch_worker = FetchWorker(upstream="origin",
                               branch=args.branch,
                               repository=router.repo,
                               read_only=read_only,
                               merge_queue=merge_queue,
                               timeout=args.fetch_timeout,
                               fetching=fetching,
                               pushing=pushing)

    merge_worker.daemon = True
    fetch_worker.daemon = True

    router.workers = [merge_worker, fetch_worker]

    if args.log == "syslog":
        handler = TimedRotatingFileHandler(args.log, when="midnight")
    else:
        handler = SysLogHandler()

    handler.setFormatter(Formatter(fmt='%(asctime)s %(message)s',
                                   datefmt='%B-%d-%Y %H:%M:%S'))

    log.addHandler(handler)

    return merge_worker, fetch_worker, router


def start_fuse():
    parser = argparse.ArgumentParser(prog='GitFS')
    args = parse_args(parser)

    merge_worker, fetch_worker, router = prepare_components(args)

    merge_worker.start()
    fetch_worker.start()

    # ready to mount it
    if sys.platform == 'darwin':
        FUSE(router, args.mount_point, foreground=args.foreground,
             allow_root=args.allow_root, allow_other=args.allow_other,
             fsname="GitFS")
    else:
        FUSE(router, args.mount_point, foreground=args.foreground,
             nonempty=True, allow_root=args.allow_root,
             allow_other=args.allow_other, fsname="GitFS")


if __name__ == '__main__':
    start_fuse()
