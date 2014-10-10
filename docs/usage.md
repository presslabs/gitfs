## Installing

```
sudo add-apt-repository ppa:presslabs/gitfs
sudo apt-get update
sudo apt-get install gitfs
```

## Mounting

Before mounting, you'll need a working git repository. You can use a [local repository](http://git-scm.com/book/en/Git-on-the-Server-Setting-Up-the-Server) or maybe use a git service like [GitHub](http://github.com).

Use `mount.fuse gitfs#http://your.com/repository.git /mount/directory` to mount your repository to the desired directory.

## Directory structure

`current/` - contains a snapshot of the commit that the branch's HEAD is pointing to. Any changes made here will be automatically committed.

`history/` - contains a series of folders whose names are dates. In these folders, you will find each commit's snapshot in another folder whose name contains the time and SHA of that commit.
