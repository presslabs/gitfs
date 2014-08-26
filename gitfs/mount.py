import argparse
from threading import RLock

from fuse import FUSE

from gitfs.utils import Args
from gitfs.routes import routes
from gitfs.router import Router
from gitfs.worker import (CommitQueue, PushQueue, CommitWorker,
                          PushWorker, PullWorker)

parser = argparse.ArgumentParser(prog='GitFS')
parser.add_argument('remote_url', help='repo to be cloned')
parser.add_argument('mount_point', help='where the repo should be mount')
parser.add_argument('-o', help='other options: repos_path, user, ' +
                               'group, branch, max_size, max_offset')
args = Args(parser)


# initialize workers and queue
commit_queue = CommitQueue()
push_queue = PushQueue()

# setting router
router = Router(remote_url=args.remote_url,
                mount_path=args.mount_point,
                repos_path=args.repos_path,
                branch=args.branch,
                user=args.user,
                group=args.group,
                max_size=args.max_size,
                max_offset=args.max_offset,
                commit_queue=commit_queue)

# register all the routes
router.register(routes)

# we need a lock for pull/push
lock = RLock()

# setup workers
commit_worker = CommitWorker(args.author_name, args.author_email,
                             args.commiter_name, args.commiter_email,
                             push_queue, commit_queue, router.repo)
push_worker = PushWorker("origin", args.branch, lock, push_queue, router.repo,
                         timeout=3)
pull_worker = PullWorker("origin", args.branch, router.repo, lock)

# start workers
push_worker.start()
commit_worker.start()
pull_worker.start()

# ready to mount it
FUSE(router, args.mount_point, foreground=args.foreground, nonempty=True,
     allow_root=args.allow_root, allow_other=args.allow_other)
