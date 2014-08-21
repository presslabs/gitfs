import argparse

from fuse import FUSE

from gitfs.utils import Args
from gitfs.routes import routes
from gitfs.router import Router
from gitfs.worker import CommitQueue, PushQueue, CommitWorker, PushWorker

parser = argparse.ArgumentParser(prog='GitFS')
parser.add_argument('remote_url', help='repo to be cloned')
parser.add_argument('mount_point', help='where the repo should be mount')
parser.add_argument('-o', help='other options: repos_path, user, ' +
                               'group, branch')
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
                commit_queue=commit_queue)

# register all the routes
router.register(routes)

# setup workers
commit_worker = CommitWorker(args.author_name, args.author_email,
                             args.commiter_name, args.commiter_email,
                             push_queue, commit_queue, router.repo)
push_worker = PushWorker("origin", args.branch, push_queue, router.repo,
                         timeout=5)
# start workers
push_worker.start()
commit_worker.start()

# ready to mount it
FUSE(router, args.mount_point, foreground=args.foreground, nonempty=True,
     allow_root=args.allow_root, allow_other=args.allow_other)
