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

import sys
from mock import MagicMock, patch, call

from six import iteritems

from gitfs.mounter import prepare_components, parse_args, start_fuse, get_credentials


class EmptyObject(object):
    def __init__(self, **kwargs):
        for name, value in iteritems(kwargs):
            setattr(self, name, value)


class TestMount(object):
    def test_prepare_components(self):
        mocked_argparse = MagicMock()
        mocked_parser = MagicMock()
        mocked_args = MagicMock()
        mocked_queue = MagicMock()
        mocked_router = MagicMock()
        mocked_routes = MagicMock()
        mocked_merger = MagicMock()
        mocked_fetcher = MagicMock()
        mocked_fuse = MagicMock()
        mocked_merge_worker = MagicMock()
        mocked_fetch_worker = MagicMock()

        args = EmptyObject(
            **{
                "remote_url": "remote_url",
                "mount_point": "mount_point",
                "username": "user",
                "current_path": "current",
                "history_path": "history",
                "password": "",
                "ssh_key": "/home/user/.ssh/id_rsa",
                "ssh_user": "user",
                "foreground": True,
                "allow_root": True,
                "allow_others": True,
                "repo_path": "repo_path",
                "branch": "branch",
                "user": "user",
                "group": "group",
                "max_size": "max_size",
                "max_offset": "max_offset",
                "upstream": "origin",
                "fetch_timeout": 10,
                "merge_timeout": 10,
                "commiter_name": "commit",
                "commiter_email": "commiter@commiting.org",
                "log": "syslog",
                "ignore_file": "",
                "module_file": "",
                "hard_ignore": None,
                "min_idle_times": 1,
                "idle_fetch_timeout": 10,
            }
        )

        mocked_argparse.Argumentparser.return_value = mocked_parser
        mocked_args.return_value = args
        mocked_merger.return_value = mocked_merge_worker
        mocked_fetcher.return_value = mocked_fetch_worker
        mocked_router.repo = "repo"
        mocked_router.repo_path = "repo_path"

        with patch.multiple(
            "gitfs.mounter",
            CommitQueue=MagicMock(return_value=mocked_queue),
            Router=MagicMock(return_value=mocked_router),
            prepare_routes=mocked_routes,
            SyncWorker=mocked_merger,
            FetchWorker=mocked_fetcher,
            FUSE=mocked_fuse,
            get_credentials=MagicMock(return_value="cred"),
        ):

            assert_result = (mocked_merge_worker, mocked_fetch_worker, mocked_router)

            assert prepare_components(args) == assert_result
            mocked_fetcher.assert_called_once_with(
                upstream="origin",
                branch="branch",
                repository="repo",
                timeout=10,
                idle_timeout=10,
                credentials="cred",
            )

            asserted_call = {
                "repository": "repo",
                "upstream": "origin",
                "branch": "branch",
                "timeout": 10,
                "repo_path": "repo_path",
                "commit_queue": mocked_queue,
                "credentials": "cred",
                "min_idle_times": 1,
            }
            mocked_merger.assert_called_once_with(
                "commit",
                "commiter@commiting.org",
                "commit",
                "commiter@commiting.org",
                **asserted_call
            )

    def test_args(self):
        mocked_parser = MagicMock()
        mocked_args = MagicMock()

        mocked_args.return_value = "args"

        with patch.multiple("gitfs.mounter", Args=mocked_args):
            assert parse_args(mocked_parser) == "args"
            asserted_calls = [
                call("remote_url", help="repo to be cloned"),
                call("mount_point", help="where the repo should be mount"),
                call(
                    "-o",
                    help="other options: repo_path, "
                    + "user, group, branch, max_size, "
                    + "max_offset, fetch_timeout, merge_timeout",
                ),
            ]
            mocked_parser.add_argument.has_calls(asserted_calls)

    def test_start_fuse(self):
        mocked_parse_args = MagicMock()
        mocked_prepare = MagicMock()
        mocked_argp = MagicMock()
        mocked_fuse = MagicMock()
        mocked_resource = MagicMock()
        mocked_args = MagicMock()

        mocked_merge = MagicMock()
        mocked_fetch = MagicMock()
        mocked_router = MagicMock()

        mocked_prepare.return_value = (mocked_merge, mocked_fetch, mocked_router)
        mocked_argp.ArgumentParser.return_value = "args"
        mocked_parse_args.return_value = mocked_args

        with patch.multiple(
            "gitfs.mounter",
            argparse=mocked_argp,
            parse_args=mocked_parse_args,
            prepare_components=mocked_prepare,
            FUSE=mocked_fuse,
            resource=MagicMock(),
        ):
            start_fuse()

            mocked_argp.ArgumentParser.assert_called_once_with(prog="GitFS")
            mocked_parse_args.assert_called_once_with("args")
            mocked_prepare.assert_called_once_with(mocked_args)

            excepted_call = {
                "foreground": mocked_args.foreground,
                "allow_root": mocked_args.allow_root,
                "allow_other": mocked_args.allow_other,
                "subtype": "gitfs",
                "fsname": mocked_args.remote_url,
            }

            if sys.platform != "darwin":
                excepted_call["nonempty"] = True

            mocked_fuse.assert_called_once_with(
                mocked_router, mocked_args.mount_point, **excepted_call
            )

    def test_get_https_credentials(self):
        mocked_user_pass = MagicMock()
        mocked_credentials = MagicMock(return_value="credentials_obj")
        mocked_args = MagicMock(password="password", username="username")

        with patch.multiple(
            "gitfs.mounter",
            UserPass=mocked_user_pass,
            RemoteCallbacks=mocked_credentials,
        ):
            assert get_credentials(mocked_args) == "credentials_obj"
            mocked_user_pass.assert_called_once_with("username", "password")

    def test_get_ssh_credentials(self):
        mocked_keypair = MagicMock()
        mocked_credentials = MagicMock(return_value="credentials_obj")
        mocked_args = MagicMock(ssh_user="user", ssh_key="key", password=None)

        with patch.multiple(
            "gitfs.mounter", Keypair=mocked_keypair, RemoteCallbacks=mocked_credentials
        ):
            assert get_credentials(mocked_args) == "credentials_obj"

            asserted_call = ("user", "key.pub", "key", "")
            mocked_keypair.assert_called_once_with(*asserted_call)
