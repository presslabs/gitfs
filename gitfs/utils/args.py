import getpass
import os
import socket
import tempfile
import grp


class Args(object):
    def __init__(self, parser):
        self.DEFAULTS = {
            "repos_path": self.get_repos_path,
            "user": self.get_current_user,
            "group": self.get_current_group,
            "foreground": True,
            "branch": "master",
            "allow_other": False,
            "allow_root": False,
            "commiter_name": self.get_current_user,
            "commiter_email": self.get_current_email,
            "max_size": 10,
            "fetch_timeout": 30,
            "merge_timeout": 5,
            "log": "syslog"
        }
        self.config = self.build_config(parser.parse_args())

    def build_config(self, args):
        if args.o:
            for arg in args.o.split(","):
                if "=" in arg:
                    item, value = arg.split("=")
                    if value == "True":
                        value = True
                    if value == "False":
                        value = False
                    setattr(args, item, value)

        args = self.set_defaults(args)

        return args

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.__dict__['config'], attr)

    def set_defaults(self, args):
        for option, value in self.DEFAULTS.iteritems():
            if not getattr(args, option, None):
                if callable(value):
                    value = value()
                setattr(args, option, value)

        return args

    def get_current_group(self):
        gid = os.getegid()
        return grp.getgrgid(gid).gr_name

    def get_current_user(self):
        return getpass.getuser()

    def get_current_email(self):
        return self.get_current_user() + "@" + socket.gethostname()

    def get_repos_path(self):
        return tempfile.mkdtemp(dir="/var/lib/gitfs")