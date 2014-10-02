gitfs [![Build Status](http://drone.presslabs.net/github.com/PressLabs/git-fs/status.svg?branch=master)](http://drone.presslabs.net/github.com/PressLabs/git-fs)
========

A FUSE filesystem for git repositories, with local cache

###Development
```bash
pip install -e .
mount.fuse gitfs#http://github.com/vtemian/testing.git /tmp/mnt -o repos_path="/tmp"
```

### MVP
Mount a repository:
* Clone it using pygit2
* Commit/Push every time a file changed
* Create regular pullls (don't use multiple threads)

### Features
* Automatically commits changes (create/delete/update) on files and their metadata
* Browse trough working index
* Browse trough commit history
* Merges with upstream by automatically accepting local changes
* Mounts the filesystem as a user/group
* Optimizes pulls by caching
* Coalesce pushes

### Mount options 
* `branch`: the branch name to follow. Defaults to `master`.
* `remote_url`: the URL of the remote. The accepted formats are:
  * https://username:password@hostname.com/repo.git - for http
  * username@hostname.com:repo.git - for ssh
* `repos_path`: the location where the repos will be cloned. Defaults to `/var/lib/gitfs/HOSTNAME/repo_path`
* `max_size`: the maximum file size in MB allowed for an individual file. If 
set to 0 then allow any file size.  The default value is __10__ MB.
* `user`: mount filesystem as this user. Defaults to `root`.
* `group`: mount filesystem as this group. Defaults to `root`.
* `commiter_name`: the name that will be displayed for all the commits. Defaults
to `user`.
* `commiter_email`: the email that will be displayed for all the commits. Defaults
to `user@FQDN`.
* `merge_timeout`: the interval between idle state and commits/pushes. 
Defaults to `5 sec`.
* `fetch_timeout`: the interval between fetches. Defaults to `30 sec`.
* `log`: The path for logging. Special name `syslog` will log to the system logger. Defaults to `syslog`.
* `foreground`: specifies whether fuse will in foreground or in backround. Defaults
to `False`.
* `allow_other`: see `man fuse`.
* `allow_root`: see `man fuse`.
