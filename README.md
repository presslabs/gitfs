gitfs [![Build Status](http://drone.presslabs.net/github.com/PressLabs/gitfs/status.svg?branch=master)](http://drone.presslabs.net/github.com/PressLabs/gitfs)
========

# Welcome to GitFS

gitfs is a [FUSE](http://fuse.sourceforge.net/) file system that fully
integrates with git. You can mount a remote repository's branch locally, and any
subsequent changes made to the files will be automatically committed to the
remote.

## What's its purpose?

gitfs was designed to bring the full powers of git to everyone, no matter how
little they know about versioning. A user can mount any repository and all the
his changes will be automatically converted into commits. gitfs will also expose
the history of the branch you're currently working on by simulating snapshots of
every commit.

gitfs is useful in places where you want to keep track of all your files, but at
the same time you don't have the possibility of organizing everything into
commits yourself. A FUSE filesystem for git repositories, with local cache

## Features
* Automatically commits changes (create/delete/update) on files and their metadata
* Browse trough working index
* Browse trough commit history
* Merges with upstream by automatically accepting local changes
* Mounts the filesystem as a user/group
* Optimizes pulls by caching
* Coalesce pushes

## Installation

### Installing from Ubuntu repository

Currently only ubuntu 12.04 and 14.04 are supported, but more versoins will be
added in the future.

```
sudo add-apt-repository ppa:presslabs/gitfs
sudo apt-get update
sudo apt-get install gitfs
```

## Usage

```
gitfs http://your.com/repository.git /mount/directory
```

### Directory structure

`current/` - contains a snapshot of the commit that the branch's HEAD is
pointing to. Any changes made here will be automatically committed.

`history/` - contains a series of folders whose names are dates. In these
folders, you will find each commit's snapshot in another folder whose name
contains the time and SHA of that commit.

### Mount options

* `branch`: the branch name to follow. Defaults to `master`.

* `remote_url`: the URL of the remote. The accepted formats are:

    * https://username:password@hostname.com/repo.git - for http
    * username@hostname.com:repo.git - for ssh

* `repos_path`: the location where the repos will be cloned. Defaults to
  `/var/lib/gitfs/HOSTNAME/repo_path`

* `max_size`: the maximum file size in MB allowed for an individual file. If set
  to 0 then allow any file size.  The default value is __10__ MB.
* `user`: mount filesystem as this user. Defaults to `root`.
* `group`: mount filesystem as this group. Defaults to `root`.
* `commiter_name`: the name that will be displayed for all the commits. Defaults
  to `user`.
* `commiter_email`: the email that will be displayed for all the commits.
  Defaults to `user@FQDN`.
* `merge_timeout`: the interval between idle state and commits/pushes. Defaults
  to `5 sec`.
* `fetch_timeout`: the interval between fetches. Defaults to `30 sec`.
* `log`: The path for logging. Special name `syslog` will log to the system
  logger. Defaults to `syslog`.
* `foreground`: specifies whether fuse will in foreground or in backround.
  Defaults to `True`.
* `allow_other`:  This option overrides the security measure restricting file
  access to the user mounting the filesystem.  So all users (including root) can
  access the files. This option is by default only allowed to root, but this
  restriction can be removed with a configuration option described in the
  previous section. Defaults to `True`
* `allow_root`: This option is similar to allow_other but file access is limited
  to the user mounting the filesystem and root. This option and allow_other are
  mutu‐ ally exclusive. Defaults to `False`

## Development

### Contributing

Development of gitfs happens at http://github.com/PressLabs/gitfs.

You are highly encouraged to contribute with code, tests, documentation or just
sharing experince.

Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## License
This project is licensed under Apache 2.0 license. Consult `LICENSE` file in the
top distribution directory for the full license text.
