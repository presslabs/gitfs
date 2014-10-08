# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
            new_value = getattr(args, option, None)

            if not new_value:
                value = value[0]

                if callable(value):
                    value = value(args)
            else:
                if value[1] == "string":
                    value = new_value
                elif value[1] == "bool":
                    if new_value.lower() == "true":
                        value = True
                    if new_value.lower() == "false":
                        value = False
                elif value[1] == "float":
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
