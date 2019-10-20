---
title: How to install and use Gitfs
linktitle: Install Gitfs
description: Here are the required steps to install and use Gitfs on your machine.
categories: [gitfs]
keywords: [gitfs, install gitfs, install on ubuntu 18.04, install on ubuntu 19.04, gitfs on ubuntu, gitfs on debian, gitfs on macos]
weight: 3
draft: false
aliases: []
toc: true
related: true
slug: install-and-use-gitfs
---

## Installing

1. Ubuntu 18.04, 19.04 and 19.10 are fully supported for now.

```
sudo add-apt-repository ppa:presslabs/gitfs
sudo apt-get update
sudo apt-get install gitfs
```

2. For using gitfs on Mac, the steps are as follows:

Prerequisites
- [Homebrew](http://brew.sh/)
```
brew install gitfs
```

### Mounting

Before mounting, you’ll need a working git repository. You can use a [local repository](http://git-scm.com/book/en/Git-on-the-Server-Setting-Up-the-Server) or maybe a git service like [GitHub](http://github.com/).

In order to mount your repository to the desired directory, use:

```
gitfs http://your.com/repository.git /mount/directory
```
#### Full github example
Consider the following setup:
- apache2 running as `www-data` user/group
- `foo_user` - your username at github.com
- `boo_password` - a password for your github's account
- `https://github.com/foo_user/my_git_project.git` - your project's URL

Before mounting your repo, run once these two commands:
- `mkdir /var/lib/gitfs`
- `mkdir /var/mount/whatever_dir`

Now it's time for test run:

`gitfs -o log=/var/log/gitfs.log,debug=true,foreground=true,commiter_name=foo_user,commiter_email=foo_user@whatever.com,user=www-data,group=www-data,username=foo_user,password=boo_password https://github.com/foo_user/my_git_project.git /var/mount/whatever_dir`

Open second terminal window and monitor the log file via command `tail -f /var/log/gitfs.log`. Play around with files in your dir and see how it reflects in your repository at github, make sure that it works in both directions. Use Ctrl-C to stop gitfs when you are done. 

For production use the following arguments:

`gitfs -o log=/var/log/gitfs.log,debug=false,foreground=false,log_level=warning,commiter_name=foo_user,commiter_email=foo_user@whatever.com,user=www-data,group=www-data,username=foo_user,password=boo_password https://github.com/foo_user/my_git_project.git /var/mount/whatever_dir`

See [Arguments](arguments.md) for more details.

### Directory structure

`current/` – contains a snapshot of the commit that the branch’s HEAD is pointing to. Any changes made here will be automatically committed and pushed to the repository you have mounted.

`history/` – contains a series of directories whose names are dates. In these directories you will find each commit’s read-only snapshot categorized by the time and SHA of that commit. Every snapshot will be read-only.

The history folder can look like this:

```shell
2014-09-15
    12:33:26-b6758e0c38
    15:52:02-68a2154362
    16:14:52-1d5e4f71ba
    16:16:40-c74a4d8078
    16:17:24-cf3f4fbad8
2014-09-17
    11:19:55-256c692b89
    14:30:25-0ab3d88431
    15:04:21-8e214eb797
2014-09-18
    11:40:06-9e154650f1
    16:05:23-cebf6b7388
```

The inner folders are the snapshots of their respective commits.

### Keeping things up to date

`gitfs` automatically fetches the newest changes from your repository at a given time interval. The default delay between fetches is `30s` but you can change this value with the `fetch_delay` argument. See [Arguments](arguments.md) for more details.


The inner folders are the snapshots of their respective commits.

### Keeping things up to date

`gitfs` automatically fetches the newest changes from your repository at a given time interval. The default delay between fetches is `30s` but you can change this value with the `fetch_delay` argument. See [Arguments](arguments.md) for more details.
