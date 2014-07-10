gitiumFS
========

A FUSE filesystem for git repositories, with local cache

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
