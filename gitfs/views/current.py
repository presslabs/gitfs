import re
import os
from stat import S_IXUSR, S_IXGRP, S_IXOTH

from gitfs.filesystems.passthrough import PassthroughFuse, STATS

from .view import View
from gitfs.log import log


class CurrentView(PassthroughFuse, View):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path
        self.dirty = {}

    def rename(self, old, new):
        new = re.sub(self.regex, '', new)
        super(CurrentView, self).rename(old, new)

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def readlink(self, path):
        return os.readlink(self._full_path(path))

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)

        attrs = dict((key, getattr(st, key)) for key in STATS)
        attrs.update({
            'st_uid': self.uid,
            'st_gid': self.gid,
        })

        return attrs

    def write(self, path, buf, offset, fh):
        result = super(CurrentView, self).write(path, buf, offset, fh)
        self.dirty[path] = {
            'message': 'Update %s' % path
        }
        return result

    def mkdir(self, path, mode):
        result = super(CurrentView, self).mkdir(path, mode)

        path = "%s/.keep" % os.path.split(path)[1]
        if not os.path.exists(path):
            fh = self.create(path, 0644)
            self.release(path, fh)

        return result

    def create(self, path, mode, fi=None):
        result = super(CurrentView, self).create(path, mode, fi)

        self.dirty[path] = {
            'message': "Created %s" % path
        }

        return result


    def chmod(self, path, mode):
        mode = int(str(oct(mode))[3:-1], 8)
        log.info("st_mode: %s", mode)
        log.info('user has exec permission: %s' % bool(mode & S_IXUSR))
        log.info('group has exec permission: %s' %  bool(mode & S_IXGRP))
        log.info('ohter have exec permission: %s' % bool(mode & S_IXOTH))
        result = super(CurrentView, self).chmod(path, mode)
        #self.dirty[path] = {
            #'message': 'chmod'
        #}
        return result

    def release(self, path, fh):
        """
        Check for path if something was written to. If so, commit and push
        the changed to upstream.
        """

        # TODO:add them into a queue and commit/push them in another thread
        if path in self.dirty:
            self.commit(path, self.dirty[path]['message'])
            del self.dirty[path]

        return os.close(fh)

    def commit(self, path, message):
        if path.startswith("/"):
            path = path[1:]

        self.repo.index.add(path)
        self.repo.commit(message, self.author, self.commiter)
        self.repo.push("origin", self.branch)
