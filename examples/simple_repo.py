from fuse import FUSE

from gitiumFS.filesystems import GitFuse


remote_url = "git://github.com/vtemian/FaceFS.git"
fs = GitFuse(remote_url)


FUSE(fs, "mnt", foreground=True)
