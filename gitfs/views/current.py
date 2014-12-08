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


import re
import os
import errno

from fuse import FuseOSError

from gitfs.utils.decorators.not_in import not_in
from gitfs.utils.decorators.write_operation import write_operation
from gitfs.log import log

from gitfs.events import writers

from .passthrough import PassthroughView, STATS


class CurrentView(PassthroughView):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.dirty = {}

    @write_operation
    @not_in("ignore", check=["old", "new"])
    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        result = super(CurrentView, self).rename(old, new)

        message = "Rename %s to %s" % (old, new)
        self._stage(**{
            'remove': os.path.split(old)[1],
            'add': new,
            'message': message
        })

        log.debug("CurrentView: Renamed %s to %s", old, new)
        return result

    @write_operation
    @not_in("ignore", check=["target"])
    def symlink(self, name, target):
        result = os.symlink(target, self.repo._full_path(name))

        message = "Create symlink to %s for %s" % (target, name)
        self._stage(add=name, message=message)

        log.debug("CurrentView: Created symlink to %s from %s", name, target)
        return result

    @write_operation
    @not_in("ignore", check=["target"])
    def link(self, name, target):
        if target.startswith('/current/'):
            target = target.replace('/current/', '/')

        result = super(CurrentView, self).link(target, name)

        message = "Create link to %s for %s" % (target, name)
        self._stage(add=name, message=message)

        log.debug("CurrentView: Created link to %s from %s", name, target)
        return result

    def readlink(self, path):
        log.debug("CurrentView: Read link %s", path)
        return os.readlink(self.repo._full_path(path))

    def getattr(self, path, fh=None):
        full_path = self.repo._full_path(path)
        status = os.lstat(full_path)

        attrs = dict((key, getattr(status, key)) for key in STATS)
        attrs.update({
            'st_uid': self.uid,
            'st_gid': self.gid,
        })

        log.debug("CurrentView: Get attributes %s for %s", str(attrs), path)
        return attrs

    @write_operation
    @not_in("ignore", check=["path"])
    def write(self, path, buf, offset, fh):
        """
            We don't like big big files, so we need to be really carefull
            with them. First we check for offset, then for size. If any of this
            is off limit, raise EFBIG error and delete the file.
        """

        if offset + len(buf) > self.max_size:
            raise FuseOSError(errno.EFBIG)

        result = super(CurrentView, self).write(path, buf, offset, fh)
        self.dirty[fh] = {
            'message': 'Update %s' % path,
        }

        log.debug("CurrentView: Wrote %s to %s", len(buf), path)
        return result

    @write_operation
    @not_in("ignore", check=["path"])
    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        keep_path = "%s/.keep" % path
        full_path = self.repo._full_path(keep_path)
        if not os.path.exists(keep_path):
            global writers
            fh = os.open(full_path, os.O_WRONLY | os.O_CREAT)
            writers += 1
            log.info("CurrentView: Open %s for write", full_path)

            super(CurrentView, self).chmod(keep_path, 0644)

            self.dirty[fh] = {
                'message': "Create the %s directory" % path,
            }

            self.release(keep_path, fh)

        log.debug("CurrentView: Created directory %s with mode %s", path, mode)

        return result

    def create(self, path, mode, fi=None):
        fh = self.open_for_write(path, os.O_WRONLY | os.O_CREAT)
        super(CurrentView, self).chmod(path, mode)

        self.dirty[fh] = {
            'message': "Created %s" % path,
        }

        log.debug("CurrentView: Created %s", path)
        return fh

    @write_operation
    @not_in("ignore", check=["path"])
    def chmod(self, path, mode):
        """
        Executes chmod on the file at os level and then it commits the change.
        """
        str_mode = ('%o' % mode)[-4:]
        if str_mode not in ['0755', '0644']:
            raise FuseOSError(errno.EINVAL)

        result = super(CurrentView, self).chmod(path, mode)

        if os.path.isdir(self.repo._full_path(path)):
            return result

        message = 'Chmod to %s on %s' % (str_mode, path)
        self._stage(add=path, message=message)

        log.debug("CurrentView: Change %s mode to %s", path,
                  ('0%o' % mode)[-4:])
        return result

    @write_operation
    @not_in("ignore", check=["path"])
    def fsync(self, path, fdatasync, fh):
        """
        Each time you fsync, a new commit and push are made
        """

        result = super(CurrentView, self).fsync(path, fdatasync, fh)

        message = 'Fsync %s' % path
        self._stage(add=path, message=message)

        log.debug("CurrentView: Fsync %s", path)
        return result

    @write_operation
    @not_in("ignore", check=["path"])
    def open_for_write(self, path, flags):
        global writers
        fh = self.open_for_read(path, flags)
        writers += 1

        log.debug("CurrentView: Open %s for write", path)
        return fh

    def open_for_read(self, path, flags):
        full_path = self.repo._full_path(path)
        log.info("CurrentView: Open %s for read", path)
        return os.open(full_path, flags)

    def open(self, path, flags):
        write_mode = flags & (os.O_WRONLY | os.O_RDWR |
                              os.O_APPEND | os.O_CREAT)
        if write_mode:
            return self.open_for_write(path, flags)
        return self.open_for_read(path, flags)

    def release(self, path, fh):
        """
        Check for path if something was written to. If so, commit and push
        the changed to upstream.
        """

        if fh in self.dirty:
            message = self.dirty[fh]['message']
            del self.dirty[fh]
            global writers
            writers -= 1
            log.debug("CurrentView: Staged %s for commit", path)
            self._stage(add=path, message=message)

        log.debug("CurrentView: Release %s", path)
        return os.close(fh)

    @write_operation
    @not_in("ignore", check=["path"])
    def rmdir(self, path):
        # Unlink the .keep file
        keep_file = os.path.join(path, '.keep')
        result = super(CurrentView, self).unlink(keep_file)

        message = 'Delete the %s directory' % path
        self._stage(remove=keep_file, message=message)

        # Delete the actual directory
        result = super(CurrentView, self).rmdir(path)

        log.debug("CurrentView: %s", message)

        return result

    @write_operation
    @not_in("ignore", check=["path"])
    def unlink(self, path):
        result = super(CurrentView, self).unlink(path)

        message = 'Deleted %s' % path
        self._stage(remove=path, message=message)

        log.debug("CurrentView: Deleted %s", path)
        return result

    def _stage(self, message, add=None, remove=None):
        non_empty = False

        if remove is not None:
            remove = self._sanitize(remove)
            if add is not None:
                add = self._sanitize(add)
                paths = self._get_files_from_path(add)
                if paths:
                    for path in paths:
                        path = path.replace("%s/" % add, "%s/" % remove)
                        self.repo.index.remove(path)
                else:
                    self.repo.index.remove(remove)
            else:
                self.repo.index.remove(remove)
            non_empty = True

        if add is not None:
            add = self._sanitize(add)
            paths = self._get_files_from_path(add)
            if paths:
                for path in paths:
                    self.repo.index.add(path)
            else:
                self.repo.index.add(add)
            non_empty = True

        if non_empty:
            self.queue.commit(add=add, remove=remove, message=message)

    def _get_files_from_path(self, path):
        paths = []

        full_path = self.repo._full_path(self._sanitize(path))
        workdir = self.repo._repo.workdir

        if os.path.isdir(full_path):
            for (dirpath, dirs, files) in os.walk(full_path):
                for filename in files:
                    paths.append("%s/%s" % (dirpath.replace(workdir, ''),
                                 filename))
        return paths

    def _sanitize(self, path):
        if path is None:
            return path

        if path.startswith("/"):
            return path[1:]

        return path
