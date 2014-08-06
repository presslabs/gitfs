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
            "allow_other": False,
            "allow_root": False,
        }
        self.config = self.build_config(parser.parse_args())

    def build_config(self, args):
        args = self.set_defaults(args)

        if args.o:
            for arg in args.o.split(","):
                if "=" in arg:
                    item, value = arg.split("=")
                    if value == "True":
                        value = True
                    if value == "False":
                        print 'is false'
                        value = False
                    setattr(args, item, value)
        return args

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.__dict__['config'], attr)

    def set_defaults(self, args):
        for option, value in self.DEFAULTS.iteritems():
            setattr(args, option, value)

        return args

    def get_current_group(self):
        gid = os.getegid()
        return grp.getgrgid(gid).gr_name

    def get_current_user(self):
        return getpass.getuser()

    def get_repos_path(self):
        return tempfile.mkdtemp()
