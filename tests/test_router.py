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

import pytest
from mock import MagicMock, patch

from fuse import FuseOSError

from gitfs.views import CurrentView
from gitfs.router import Router


class TestRouter(object):
    def get_new_router(self):
        mocked_credentials = MagicMock()
        mocked_branch = MagicMock()
        mocked_repo = MagicMock()
        mocked_repository = MagicMock()
        mocked_log = MagicMock()
        mocked_ignore = MagicMock()
        mocked_cache_ignore = MagicMock()
        mocked_lru = MagicMock()
        mocked_pwnam = MagicMock()
        mocked_grnam = MagicMock()
        mocked_time = MagicMock()
        mocked_queue = MagicMock()
        mocked_shutil = MagicMock()
        mocked_shutting = MagicMock()
        mocked_fetch = MagicMock()

        mocked_time.time.return_value = 0
        mocked_repository.clone.return_value = mocked_repo
        mocked_ignore.return_value = mocked_cache_ignore
        mocked_pwnam.return_value.pw_uid = 1
        mocked_grnam.return_value.gr_gid = 1

        mocks = {
            'repository': mocked_repository,
            'repo': mocked_repo,
            'log': mocked_log,
            'ignore': mocked_ignore,
            'ignore_cache': mocked_ignore,
            'lru': mocked_lru,
            'getpwnam': mocked_pwnam,
            'getgrnam': mocked_grnam,
            'time': mocked_time,
            'queue': mocked_queue,
            'shutil': mocked_shutil,
            'shutting': mocked_shutting,
            'fetch': mocked_fetch,
        }

        init_kwargs = {
            'remote_url': 'remote_url',
            'repo_path': 'repository_path',
            'mount_path': 'mount_path',
            'credentials': mocked_credentials,
            'branch': mocked_branch,
            'user': 'user',
            'group': 'root',
            'commit_queue': mocked_queue,
            'max_size': 10,
            'max_offset': 10,
            'ignore_file': '',
            'module_file': '',
            'hard_ignore': None,
        }

        with patch.multiple('gitfs.router', Repository=mocked_repository,
                            log=mocked_log, CachedIgnore=mocked_ignore,
                            lru_cache=mocked_lru, getpwnam=mocked_pwnam,
                            getgrnam=mocked_grnam, time=mocked_time,
                            shutil=mocked_shutil, fetch=mocked_fetch,
                            shutting_down=mocked_shutting):
            router = Router(**init_kwargs)

        mocks.update(init_kwargs)
        return router, mocks

    def test_constructor(self):
        router, mocks = self.get_new_router()

        asserted_call = (mocks['remote_url'], mocks['repo_path'],
                         mocks['branch'], mocks['credentials'])
        mocks['repository'].clone.assert_called_once_with(*asserted_call)
        mocks['ignore'].assert_called_once_with(**{
            'ignore': 'repository_path/.gitignore',
            'exclude': None,
            'hard_ignore': None,
            'submodules': 'repository_path/.gitmodules'
        })
        mocks['getpwnam'].assert_called_once_with(mocks['user'])
        mocks['getgrnam'].assert_called_once_with(mocks['group'])

        assert mocks['repo'].commits.update.call_count == 1
        assert mocks['time'].time.call_count == 1
        assert router.commit_queue == mocks['queue']
        assert router.max_size == 10
        assert router.max_offset == 10

    def test_init(self):
        mocked_fetch = MagicMock()
        mocked_sync = MagicMock()

        router, mocks = self.get_new_router()
        router.workers = [mocked_fetch, mocked_sync]

        router.init("path")

        assert mocked_fetch.start.call_count == 1
        assert mocked_sync.start.call_count == 1

    def test_destroy(self):
        mocked_fetch = MagicMock()
        mocked_sync = MagicMock()

        router, mocks = self.get_new_router()
        router.workers = [mocked_fetch, mocked_sync]

        with patch.multiple('gitfs.router', shutil=mocks['shutil'],
                            fetch=mocks['fetch'],
                            shutting_down=mocks['shutting']):
            router.destroy("path")

        assert mocked_fetch.join.call_count == 1
        assert mocked_sync.join.call_count == 1
        assert mocks['fetch'].set.call_count == 1
        assert mocks['shutting'].set.call_count == 1
        mocks['shutil'].rmtree.assert_called_once_with(mocks['repo_path'])

    def test_call_with_invalid_operation(self):
        router, mocks = self.get_new_router()

        router.register([("/", CurrentView)])
        with patch('gitfs.router.lru_cache') as mocked_cache:
            mocked_cache.get_if_exists.return_value = None
            with pytest.raises(FuseOSError):
                router("random_operation", "/")

    def test_call_with_valid_operation(self):
        mocked_view = MagicMock()
        mocked_cache = MagicMock()
        mocked_idle_event = MagicMock()

        router, mocks = self.get_new_router()

        router.register([("/", MagicMock(return_value=mocked_view))])
        with patch.multiple('gitfs.router',
                            idle=mocked_idle_event, lru_cache=mocked_cache):
            mocked_cache.get_if_exists.return_value = None
            result = router("random_operation", "/")

            assert result == mocked_view.random_operation("/")
            assert mocked_idle_event.clear.call_count == 1

    def test_call_with_init(self):
        mocked_init = MagicMock()

        router, mocks = self.get_new_router()
        router.init = mocked_init
        assert router('init', "/") == mocked_init("/")

    def test_get_missing_view(self):
        router, mocks = self.get_new_router()

        with pytest.raises(ValueError):
            router.get_view("/")

    def test_get_view(self):
        mocked_index = MagicMock()
        mocked_current = MagicMock()
        mocked_view = MagicMock(return_value=mocked_current)

        router, mocks = self.get_new_router()

        router.register([
            ("/history", mocked_view),
            ("/current", mocked_view),
            ("/", MagicMock(return_value=mocked_index)),
        ])
        with patch('gitfs.router.lru_cache') as mocked_cache:
            mocked_cache.get_if_exists.return_value = None

            view, path = router.get_view("/current")
            assert view == mocked_current
            assert path == "/"
            asserted_call = {
                'repo': mocks['repo'],
                'ignore': mocks['repo'].ignore,
                'repo_path': mocks['repo_path'],
                'mount_path': mocks['mount_path'],
                'regex': "/current",
                'relative_path': "/",
                'uid': 1,
                'gid': 1,
                'branch': mocks['branch'],
                'mount_time': 0,
                'queue': mocks['queue'],
                'max_size': mocks['max_size'],
                'max_offset': mocks['max_offset'],
            }
            mocked_view.assert_called_once_with(**asserted_call)
            mocked_cache.get_if_exists.assert_called_once_with("/current")

    def test_get_view_from_cache(self):
        mocked_index = MagicMock()

        router, mocks = self.get_new_router()

        router.register([
            ("/", MagicMock(return_value=mocked_index)),
        ])
        with patch('gitfs.router.lru_cache') as mocked_cache:
            mocked_cache.get_if_exists.return_value = mocked_index

            view, path = router.get_view("/")
            assert view == mocked_index
            assert path == "/"

    def test_getattr_special_method(self):
        router, mocks = self.get_new_router()
        assert router.bmap is False
        assert router.read is not False
