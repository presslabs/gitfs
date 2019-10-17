# Copyright 2014-2016 Presslabs SRL
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


from mock import MagicMock, patch, call

from six import iteritems

from gitfs.utils.args import Args


class TestArgs(object):
    def test_args(self):
        mocked_os = MagicMock()
        mocked_log = MagicMock()
        mocked_grp = MagicMock()
        mocked_pass = MagicMock()
        mocked_file = MagicMock()
        mocked_args = MagicMock()
        mocked_parser = MagicMock()
        mocked_urlparse = MagicMock()
        mocked_parse_res1 = MagicMock()
        mocked_parse_res2 = MagicMock()
        mocked_log_handler = MagicMock()
        url = "user@domain.com:owner/test.git"

        mocked_file.mkdtemp.return_value = "/tmp"
        mocked_pass.getuser.return_value = "test_user"
        mocked_os.getgid.return_value = 1
        mocked_os.environ = {}
        mocked_os.path.abspath.return_value = "abs/tmp"
        mocked_grp.getgrgid().gr_name = "test_group"
        mocked_parser.parse_args.return_value = mocked_args
        mocked_args.remote_url = url
        mocked_parse_res1.scheme = None
        mocked_parse_res2.username = "user"
        mocked_urlparse.side_effect = [mocked_parse_res1, mocked_parse_res2]
        mocked_args.o = "magic=True,not_magic=False"
        mocked_args.group = None
        mocked_args.repo_path = None
        mocked_args.user = None
        mocked_args.branch = None
        mocked_args.ssh_user = None
        mocked_args.sentry_dsn = ""

        with patch.multiple(
            "gitfs.utils.args",
            os=mocked_os,
            grp=mocked_grp,
            getpass=mocked_pass,
            tempfile=mocked_file,
            TimedRotatingFileHandler=mocked_log_handler,
            urlparse=mocked_urlparse,
            log=mocked_log,
        ):

            args = Args(mocked_parser)
            asserted_results = {
                "repo_path": "abs/tmp",
                "user": "test_user",
                "group": "test_group",
                "branch": "master",
                "not_magic": "False",
                "ssh_user": "user",
            }
            for name, value in iteritems(asserted_results):
                assert value == getattr(args, name)

            assert args.config == mocked_args
            assert mocked_pass.getuser.call_count == 1
            assert mocked_file.mkdtemp.call_count == 1
            mocked_log.setLevel.assert_called_once_with("DEBUG")
            mocked_urlparse.assert_has_calls([call(url), call("ssh://" + url)])
            mocked_grp.getgrgid.has_calls([call(1)])
