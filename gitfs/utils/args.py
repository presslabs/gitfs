import os
import grp
import getpass
import tempfile


class Args(object):
    def __init__(self, parser):
        self.DEFAULTS = {
            "repos_path": self.get_repos_path(),
            "user": self.get_current_user(),
            "group": self.get_current_group(),
            "foreground": True,
            "branch": "master",
        }
        self.config = self.build_config(parser.parse_args())

    def build_config(self, args):
        args = self.set_defaults(args)

        if args.o:
            for arg in args.o.split(","):
                if "=" in arg:
                    item, value = arg.split("=")
                    setattr(args, item, value)
        return args

    def set_defaults(self, args):
        for option, value in self.DEFAULTS.iteritems():
            setattr(args, option, value)

        return args

    def get_current_grop(self):
        gid = os.getegid()
        return grp.getgrgid(gid).gr_name

    def get_current_user(self):
        return getpass.getuser()

    def get_repos_path(self):
        return tempfile.mkdtemp()
