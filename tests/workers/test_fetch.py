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
from mock import patch, MagicMock

from gitfs.worker.fetch import FetchWorker


class TestFetchWorker(object):
    def test_work(self):
        mocked_peasant = MagicMock()
        mocked_fetch = MagicMock(side_effect=ValueError)
        mocked_fetch_event = MagicMock()

        with patch.multiple('gitfs.worker.fetch', Peasant=mocked_peasant,
                            fetch=mocked_fetch_event):
            worker = FetchWorker()
            worker.fetch = mocked_fetch
            worker.timeout = 5

            with pytest.raises(ValueError):
                worker.work()

            assert mocked_fetch.call_count == 1
            mocked_fetch_event.wait.assert_called_once_with(5)

    def test_fetch_remote_is_down(self):
        mocked_fetch_ok = MagicMock()
        mocked_fetch = MagicMock()
        mocked_repo = MagicMock()

        mocked_repo.fetch = MagicMock(side_effect=ValueError)
        mocked_fetch_ok.set.side_effect = ValueError

        with patch.multiple('gitfs.worker.fetch',
                            fetch_successful=mocked_fetch_ok,
                            fetch=mocked_fetch):
            worker = FetchWorker(repository=mocked_repo,
                                 upstream="origin",
                                 credentials="credentials",
                                 branch="master")
            worker.fetch()

            mocked_repo.fetch.assert_called_once_with("origin", "master",
                                                      "credentials")
            assert mocked_fetch_ok.clear.call_count == 1
            assert mocked_fetch.clear.call_count == 1

    def test_fetch_in_idle_mode(self):
        mocked_peasant = MagicMock()
        mocked_fetch = MagicMock(side_effect=ValueError)
        mocked_fetch_event = MagicMock()
        mocked_idle = MagicMock()

        mocked_idle.is_set.return_value = True

        with patch.multiple('gitfs.worker.fetch', Peasant=mocked_peasant,
                            fetch=mocked_fetch_event, idle=mocked_idle):
            worker = FetchWorker()
            worker.fetch = mocked_fetch
            worker.timeout = 5
            worker.idle_timeout = 20

            with pytest.raises(ValueError):
                worker.work()

            assert mocked_fetch.call_count == 1
            mocked_fetch_event.wait.assert_called_once_with(20)
