def parse_args(parser):
    args = parser.parse_args()
    args = set_defaults(args)

    if args.o:
        for arg in args.o.split(","):
            if "=" in arg:
                item, value = arg.split("=")
                setattr(args, item, value)
    return args


def set_defaults(args):
    # TODO: get currrent user + group
    # TODO: generate random tmp dir

    defaults = {
        "repos_path": "/tmp/repos",
        "user": "root",
        "group": "root",
        "foreground": True,
        "branch": "master",
    }
    for option, value in defaults.iteritems():
        setattr(args, option, value)
    return args
