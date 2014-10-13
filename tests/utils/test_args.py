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
        mocked_log_handler = MagicMock()

        mocked_file.mkdtemp.return_value = "/tmp"
        mocked_pass.getuser.return_value = "test_user"
        mocked_os.getgid.return_value = 1
        mocked_grp.getgrgid().gr_name = "test_group"
        mocked_parser.parse_args.return_value = mocked_args
        mocked_args.o = "magic=True,not_magic=False"
        mocked_args.group = None
        mocked_args.repos_path = None
        mocked_args.user = None
        mocked_args.branch = None

        with patch.multiple('gitfs.utils.args', os=mocked_os, grp=mocked_grp,
                            getpass=mocked_pass, tempfile=mocked_file,
                            TimedRotatingFileHandler=mocked_log_handler):

            args = Args(mocked_parser)
            asserted_results = {
                "repos_path": "/tmp",
                "user": "test_user",
                "group": "test_group",
                "branch": "master",
                "not_magic": "False",
            }
            for name, value in asserted_results.iteritems():
                assert value == getattr(args, name)

            assert args.config == mocked_args
            assert mocked_pass.getuser.call_count == 1
            assert mocked_file.mkdtemp.call_count == 1
            mocked_grp.getgrgid.has_calls([call(1)])
