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


import os
from threading import Event

import pytest
from mock import patch, MagicMock, call

from fuse import FuseOSError
from gitfs.views.current import CurrentView
from gitfs.cache.gitignore import CachedIgnore


class TestCurrentView(object):
    def test_rename(self):
        mocked_re = MagicMock()
        mocked_index = MagicMock()
        mocked_os = MagicMock()
        mocked_result = MagicMock()

        mocked_result.rename.return_value = True
        mocked_re.sub.return_value = "new"
        mocked_os.path.split.return_value = [1, 1]

        with patch.multiple('gitfs.views.current', re=mocked_re,
                            os=mocked_os):
            from gitfs.views import current as current_view
            old_rename = current_view.PassthroughView.rename
            current_view.PassthroughView.rename = lambda self, old, new: True

            current = CurrentView(regex="regex", repo_path="repo_path",
                                  ignore=CachedIgnore("f"))
            current._stage = mocked_index

            result = current.rename("old", "new")
            assert result is True
            mocked_index.assert_called_once_with(**{
                'remove': 1,
                'add': "new",
                "message": "Rename old to new"
            })
            mocked_os.path.split.assert_called_once_with("old")
            current_view.PassthroughView.rename = old_rename

    def test_rename_in_git_dir(self):
        current = CurrentView(repo_path="repo",
                              ignore=CachedIgnore("f"))
        with pytest.raises(FuseOSError):
            current.rename(".git/", ".git/")

    def test_symlink(self):
        mocked_index = MagicMock()
        mocked_full_path = MagicMock()

        mocked_full_path.return_value = "full_path"

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.symlink.return_value = "done"

            current = CurrentView(repo_path="repo",
                                  ignore=CachedIgnore("f"))
            current._stage = mocked_index
            current._full_path = mocked_full_path

            assert current.symlink("name", "target") == "done"
            mocked_os.symlink.assert_called_once_with("target", "full_path")
            mocked_full_path.assert_called_once_with("name")
            message = "Create symlink to target for name"
            mocked_index.assert_called_once_with(add="name", message=message)

    def test_readlink(self):
        mocked_full_path = MagicMock()
        mocked_full_path.return_value = "full path"

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.readlink.return_value = "done"

            current = CurrentView(repo_path="repo",
                                  ignore=CachedIgnore("f"))
            current._full_path = mocked_full_path

            assert current.readlink("path") == "done"

    def test_getattr(self):
        mocked_full = MagicMock()
        mocked_os = MagicMock()
        mocked_stat = MagicMock()

        mocked_stat.simple = "stat"
        mocked_os.lstat.return_value = mocked_stat
        mocked_full.return_value = "full_path"

        with patch.multiple('gitfs.views.current', os=mocked_os,
                            STATS=['simple']):
            current = CurrentView(repo_path="repo", uid=1, gid=1,
                                  ignore=CachedIgnore("f"))
            current._full_path = mocked_full

            result = current.getattr("path")
            asserted_result = {
                'st_uid': 1,
                'st_gid': 1,
                'simple': "stat"
            }
            assert result == asserted_result

            mocked_os.lstat.assert_called_once_with("full_path")
            mocked_full.assert_called_once_with("path")

    def test_write_in_git_dir(self):
        with pytest.raises(FuseOSError):
            current = CurrentView(repo_path="repo", uid=1, gid=1,
                                  read_only=Event(),
                                  ignore=CachedIgnore("f"))
            current.write(".git/index", "buf", "offset", 1)

    def test_write_to_large_file(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), ignore=CachedIgnore("f"))
        current.max_size = 10
        current.dirty = {
            '/path': {
                'size': 5
            }
        }

        with pytest.raises(FuseOSError):
            current.write("/path", "bufffffert", 11, 1)

    def test_write(self):
        from gitfs.views import current as current_view
        mocked_write = lambda self, path, buf, offste, fh: "done"
        old_write = current_view.PassthroughView.write
        current_view.PassthroughView.write = mocked_write

        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              read_only=Event(), ignore=CachedIgnore("f"))
        current.max_offset = 20
        current.max_size = 20
        current.dirty = {
            1: {}
        }

        assert current.write("/path", "buf", 3, 1) == "done"
        assert current.dirty == {
            1: {
                'message': 'Update /path',
            }
        }
        current_view.PassthroughView.write = old_write

    def test_mkdir(self):
        from gitfs.views import current as current_view
        old_mkdir = current_view.PassthroughView.mkdir
        mocked_mkdir = lambda self, path, mode: "done"
        current_view.PassthroughView.mkdir = mocked_mkdir

        mocked_create = MagicMock()
        mocked_create.return_value = 1
        mocked_release = MagicMock()

        with patch('gitfs.views.current.os') as mocked_os:
            mocked_os.path.exists.return_value = False

            current = CurrentView(repo_path="repo", uid=1, gid=1,
                                  ignore=CachedIgnore("f"))
            current.create = mocked_create
            current.release = mocked_release

            assert current.mkdir("/path", "mode") == "done"
            mocked_os.path.exists.assert_called_once_with("/path/.__keep__gitfs__")
            mocked_create.assert_called_once_with("/path/.__keep__gitfs__", 0644)
            mocked_release.assert_called_once_with("/path/.__keep__gitfs__", 1)
        current_view.PassthroughView.mkdir = old_mkdir

    def test_mkdir_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))
        with pytest.raises(FuseOSError):
            current.mkdir(".git/", "mode")

    def test_create_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))

        with pytest.raises(FuseOSError):
            current.create(".git/", "mode")

    def test_create(self):
        from gitfs.views import current as current_view
        old_chmod = current_view.PassthroughView.chmod
        mock_chmod = lambda self, path, mode: "done"
        current_view.PassthroughView.chmod = mock_chmod

        mocked_open = MagicMock()
        mocked_open.return_value = "done"
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))
        current.dirty = {
            '/path': {
                'content': "here"
            }
        }
        current.open_for_write = mocked_open

        assert current.create("/path", "mode") == "done"
        current_view.PassthroughView.chmod = old_chmod

    def test_chmod_in_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))
        with pytest.raises(FuseOSError):
            current.chmod(".git/", "mode")

    def test_chmod(self):
        from gitfs.views import current as current_view
        old_chmod = current_view.PassthroughView.chmod
        current_view.PassthroughView.chmod = lambda self, path, mode: "done"

        mocked_index = MagicMock()

        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))

        current._stage = mocked_index

        assert current.chmod("/path", 0644) == "done"
        message = 'Chmod to %s on %s' % (str(oct(0644))[-4:], "/path")
        mocked_index.assert_called_once_with(add="/path", message=message)

        current_view.PassthroughView.chmod = old_chmod

    def test_fsync_a_file_from_git_dir(self):
        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))

        with pytest.raises(FuseOSError):
            current.fsync(".git/", "data", 0)

    def test_fsync(self):
        from gitfs.views import current as current_view
        old_fsync = current_view.PassthroughView.fsync
        current_view.PassthroughView.fsync = lambda me, path, data, fh: "done"

        mocked_index = MagicMock()

        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))
        current._stage = mocked_index

        assert current.fsync("/path", "data", 1) == "done"
        message = "Fsync /path"
        mocked_index.assert_called_once_with(add="/path", message=message)

        current_view.PassthroughView.fsync = old_fsync

    def test_unlink_from_git_dir(self):
        current = CurrentView(repo_path="repo", ignore=CachedIgnore("f"))

        with pytest.raises(FuseOSError):
            current.unlink(".git/")

    def test_unlink(self):
        from gitfs.views import current as current_view
        old_unlink = current_view.PassthroughView.unlink
        current_view.PassthroughView.unlink = lambda me, path: "done"

        mocked_index = MagicMock()

        current = CurrentView(repo_path="repo", uid=1, gid=1,
                              ignore=CachedIgnore("f"))
        current._stage = mocked_index

        assert current.unlink("/path") == "done"
        message = "Deleted /path"
        mocked_index.assert_called_once_with(remove="/path", message=message)

        current_view.PassthroughView.unlink = old_unlink

    def test_stage(self):
        mocked_repo = MagicMock()
        mocked_sanitize = MagicMock()
        mocked_queue = MagicMock()

        mocked_sanitize.return_value = ["to-stage"]

        current = CurrentView(repo_path="repo", repo=mocked_repo,
                              queue=mocked_queue, ignore=CachedIgnore("f"))
        current._sanitize = mocked_sanitize
        current._stage("message", ["add"], ["remove"])

        mocked_queue.commit.assert_called_once_with(add=['to-stage'],
                                                    remove=['to-stage'],
                                                    message="message")
        mocked_repo.index.add.assert_called_once_with(["to-stage"])
        mocked_repo.index.remove.assert_called_once_with(["to-stage"])

        mocked_sanitize.has_calls([call(['add']), call(['remove'])])

    def test_sanitize(self):
        current = CurrentView(repo_path="repo")
        assert current._sanitize("/path") == "path"

    def test_open(self):
        mocked_full = MagicMock()
        mocked_os = MagicMock()

        mocked_os.open.return_value = 1
        mocked_full.return_value = "full_path"

        with patch.multiple('gitfs.views.current', os=mocked_os):
            current = CurrentView(repo_path="repo",
                                  ignore=CachedIgnore("f"))

            current._full_path = mocked_full
            current.writing = set([])

            assert current.open("path/", os.O_WRONLY) == 1
            mocked_os.open.assert_called_once_with("full_path", os.O_WRONLY)

    def test_release(self):
        message = "I need to stage this"
        mocked_os = MagicMock()
        mocked_stage = MagicMock()

        mocked_os.close.return_value = 0

        with patch.multiple('gitfs.views.current', os=mocked_os):
            current = CurrentView(repo_path="repo",
                                  ignore=CachedIgnore("f"))
            current._stage = mocked_stage
            current.dirty = {
                4: {
                    'message': message
                }
            }

            assert current.release("/path", 4) == 0

            mocked_os.close.assert_called_once_with(4)
            mocked_stage.assert_called_once_with(add="/path", message=message)
