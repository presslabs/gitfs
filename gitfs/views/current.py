import re
import os

from pygit2 import Signature

from gitfs.filesystems.passthrough import PassthroughFuse, STATS

from .view import View


class CurrentView(View, PassthroughFuse):

    def __init__(self, *args, **kwargs):
        super(CurrentView, self).__init__(*args, **kwargs)
        self.root = self.repo_path
        self.dirty = set([])

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
        self.dirty.add(path)
        return result

    def release(self, path, fh):
        if path in self.dirty:
            self.repo.index.add(path)
            self._create_commit("Update %s" % path, self.author, self.commiter)
            self.dirty.remove(path)
        return os.close(fh)

    def _create_commit(self, message, author, commiter, ref="HEAD"):
        # sign the author
        commit_author = Signature(author[0], author[1])
        commiter = Signature(commiter[0], commiter[1])

        # write index localy
        tree = self.repo.index.write_tree()
        self.repo.index.write()

        # get parent
        parent = self.repo.revparse_single(ref)
        return self.repo.create_commit(ref, commit_author, commiter, message,
                                       tree, [parent.id])
