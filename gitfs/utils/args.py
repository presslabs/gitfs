def parse_args(parser):
    args = parser.parse_args()
    args = set_defaults(args)

    for arg in args.o.split(","):
        if "=" in arg:
            item, value = arg.split("=")
            setattr(args, item, value)
    return args


def set_defaults(args):
    defaults = {
        "repos_path": "/tmp/gitfs/repos",
        "user": "root",
        "group": "root",
        "foreground": True,
        "branch": "master",
    }
    for option, value in defaults.iteritems():
        setattr(args, option, value)
    return args
