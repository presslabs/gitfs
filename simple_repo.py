from gitiumFS.filesystems import GitFuse

remote_url = "git@github.com:vtemian/FaceFS.git"
fs = GitFuse(remote_url)
