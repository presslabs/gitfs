import getpass
import os
import socket
import tempfile
import grp
from collections import OrderedDict


class Args(object):
    def __init__(self, parser):
        self.DEFAULTS = OrderedDict({
            "repos_path": (self.get_repos_path, "string"),
            "user": (self.get_current_user, "string"),
            "group": (self.get_current_group, "string"),
            "foreground": (True, "bool"),
            "branch": ("master", "string"),
            "allow_other": (False, "bool"),
            "allow_root": (False, "bool"),
            "commiter_name": (self.get_current_user, "string"),
            "commiter_email": (self.get_current_email, "string"),
            "max_size": (10, "float"),
            "fetch_timeout": (30, "float"),
            "merge_timeout": (5, "float"),
            "log": ("syslog", "string")
        })
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
                    value = value(args)
            else:
                if value[1] == "string":
                    value = new_value
                if value[1] == "bool":
                    if new_value == "True":
                        value = True
                    if new_value == "False":
                        value = False
                if value[1] == "float":
                    value = float(new_value)

            setattr(args, option, value)

        return args

    def get_current_group(self, args):
        gid = os.getegid()
        return grp.getgrgid(gid).gr_name

    def get_current_user(self, args):
        return getpass.getuser()

    def get_current_email(self, args):
        return "%s@%s" % (args.user, socket.gethostname())

    def get_repos_path(self, args):
        return tempfile.mkdtemp(dir="/var/lib/gitfs")
