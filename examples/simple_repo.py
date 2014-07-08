from fuse import FUSE

from gitiumFS.filesystems import GitFuse


remote_url = "https://github.com/vtemian/FaceFS.git"
fs = GitFuse(remote_url)


FUSE(fs, "mnt", foreground=True)
