gitiumFS
========

A FUSE filesystem for git repositories, with local cache

### MVP
Mount a repository:
* Clone it using pygit2
* Commit/Push every time a file changed
* Create regular pullls (don't use multiple threads)
