import getpass
import os
import socket
import tempfile
import grp


class Args(object):
    def __init__(self, parser):
        self.DEFAULTS = {
            "repos_path": (self.get_repos_path, "s"),
            "user": (self.get_current_user, "s"),
            "group": (self.get_current_group, "s"),
            "foreground": (True, "b"),
            "branch": ("master", "s"),
            "allow_other": (False, "b"),
            "allow_root": (False, "b"),
            "commiter_name": (self.get_current_user, "s"),
            "commiter_email": (self.get_current_email, "s"),
            "max_size": (10, "f"),
            "fetch_timeout": (30, "f"),
            "merge_timeout": (5, "f"),
            "log": ("syslog", "s")
        }
        self.config = self.build_config(parser.parse_args())

    def build_config(self, args):
        if args.o:
            for arg in args.o.split(","):
                if "=" in arg:
                    item, value = arg.split("=")

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
            new_value = getattr(args, option, None)

            if not new_value:
                value = value[0]

                if callable(value):
                    value = value()
            else:
                if value[1] == "s":
                    value = new_value
                if value[1] == "b":
                    if new_value == "True":
                        value = True
                    if new_value == "False":
                        value = False
                if value[1] == "f":
                    value = float(new_value)

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
