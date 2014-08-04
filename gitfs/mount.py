import argparse

from fuse import FUSE

from router import Router
from routes import routes

parser = argparse.ArgumentParser(prog='GitFS')
parser.add_argument('remote_url', help='repo to be cloned')
parser.add_argument('mount_point', help='where the repo should be mount')
parser.add_argument('--repos_path', default="/tmp/gitfs/repos",
                    help="A path representing where to keep cloned repos")
parser.add_argument('--branch', default="master",
                    help="Specific which branch to follow. The default is " +
                    "to use the remote's default branch.")
parser.add_argument("--foreground", help="Start in foreground or not",
                    default=True)
args = parser.parse_args()

# setting router
router = Router(remote_url=args.remote_url,
                repos_path=args.repos_path,
                mount_path=args.mount_point)
# register all the routes
router.register(routes)

# ready to mount it
FUSE(router, args.mount_point, foreground=args.foreground, nonempty=True)
