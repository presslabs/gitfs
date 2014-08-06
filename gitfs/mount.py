import argparse

from fuse import FUSE

from gitfs.router import Router
from gitfs.routes import routes
from gitfs.utils import Args

parser = argparse.ArgumentParser(prog='GitFS')
parser.add_argument('remote_url', help='repo to be cloned')
parser.add_argument('mount_point', help='where the repo should be mount')
parser.add_argument('-o', help='other options: repos_path, user, ' +
                               'group, branch')
args = Args(parser)

# setting router
router = Router(remote_url=args.remote_url,
                mount_path=args.mount_point,
                repos_path=args.repos_path,
                branch=args.branch,
                user=args.user,
                group=args.group,
                commiter_name=args.commiter_name,
                commiter_email=args.commiter_email,
                author_name=args.author_name,
                author_email=args.author_email)

# register all the routes
router.register(routes)

# ready to mount it
FUSE(router, args.mount_point, foreground=args.foreground, nonempty=True,
     allow_root=args.allow_root, allow_other=args.allow_other)
