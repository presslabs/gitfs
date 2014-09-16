from mock import MagicMock, patch, call

from gitfs.utils.args import Args


class TestArgs(object):
    def test_args(self):
        mocked_parser = MagicMock()
        mocked_args = MagicMock()
        mocked_os = MagicMock()
        mocked_grp = MagicMock()
        mocked_pass = MagicMock()
        mocked_file = MagicMock()

        mocked_file.mkdtemp.return_value = "/tmp"
        mocked_pass.getuser.return_value = "test_user"
        mocked_os.getgid.return_value = 1
        mocked_grp.getgrgid().gr_name = "test_group"
        mocked_parser.parse_args.return_value = mocked_args
        mocked_args.o = "magic=True,not_magic=False"

        with patch.multiple('gitfs.utils.args', os=mocked_os, grp=mocked_grp,
                            getpass=mocked_pass, tempfile=mocked_file):

            args = Args(mocked_parser)
            asserted_results = {
                "repos_path": "/tmp",
                "user": "test_user",
                "group": "test_group",
                "foreground": True,
                "branch": "master",
                "upstream": "origin",
                "allow_other": False,
                "allow_root": False,
                "author_name": "Presslabs",
                "author_email": "git@presslabs.com",
                "commiter_name": "Presslabs",
                "commiter_email": "git@presslabs.com",
                "max_size": 10 * 1024 * 1024,
                "max_offset": 10 * 1024 * 1024,
                "fetch_timeout": 5,
                "merge_timeout": 2,
                "magic": True,
                "not_magic": False,
            }
            for name, value in asserted_results.iteritems():
                assert value == getattr(args, name)

            assert args.config == mocked_args
            assert mocked_pass.getuser.call_count == 1
            assert mocked_file.mkdtemp.call_count == 1
            mocked_grp.getgrgid.has_calls([call(1)])
