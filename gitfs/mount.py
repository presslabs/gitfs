import argparse

from fuse import FUSE

from gitfs.router import Router
from gitfs.routes import routes
from gitfs.utils import parse_args

parser = argparse.ArgumentParser(prog='GitFS')
parser.add_argument('remote_url', help='repo to be cloned')
parser.add_argument('mount_point', help='where the repo should be mount')
parser.add_argument('-o', help='other options: repos_path, user, ' +
                               'group, branch')
args = parse_args(parser)

# setting router
router = Router(remote_url=args.remote_url,
                mount_path=args.mount_point,
                repos_path=args.repos_path,
                branch=args.branch,
                user=args.user,
                group=args.group)

# register all the routes
router.register(routes)

# ready to mount it
FUSE(router, args.mount_point, foreground=args.foreground, nonempty=True)
