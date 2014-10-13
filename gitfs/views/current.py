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
        result = os.symlink(target, self._full_path(name))

        message = "Create symlink to %s for %s" % (target, name)
        self._stage(add=name, message=message)

        log.debug("CurrentView: Created symlink to %s from %s", name, target)
        return result

    def readlink(self, path):
        log.debug("CurrentView: Read link %s", path)
        return os.readlink(self._full_path(path))

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)

        attrs = dict((key, getattr(st, key)) for key in STATS)
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
        log.debug("CurrentView: Created directory %s with mode %s", path, mode)

        path = "%s/.keep" % os.path.split(path)[1]
        if not os.path.exists(path):
            fh = self.create(path, 0644)
            self.release(path, fh)

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

        result = super(CurrentView, self).chmod(path, mode)

        message = 'Chmod to %s on %s' % (str(oct(mode))[3:-1], path)
        self._stage(add=path, message=message)

        log.debug("CurrentView: Change %s mode to %s", path,
                  str(oct(mode))[3:-1])
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
        full_path = self._full_path(path)
        log.info("Open %s for read", path)
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
    def unlink(self, path):
        result = super(CurrentView, self).unlink(path)

        message = 'Deleted %s' % path
        self._stage(remove=path, message=message)

        log.debug("CurrentView: Deleted %s", path)
        return result

    def _stage(self, message, add=None, remove=None):
        non_empty = False

        add = self._sanitize(add)
        remove = self._sanitize(remove)

        if remove is not None:
            self.repo.index.remove(self._sanitize(remove))
            non_empty = True

        if add is not None:
            self.repo.index.add(self._sanitize(add))
            non_empty = True

        if non_empty:
            self.queue.commit(add=add, remove=remove, message=message)

    def _sanitize(self, path):
        if path is not None and path.startswith("/"):
            path = path[1:]
        return path
