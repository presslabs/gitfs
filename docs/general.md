## Welcome to gitfs

gitfs is a [FUSE](http://fuse.sourceforge.net/) file system that fully integrates with git. You can mount a remote repository’s branch locally, and any subsequent changes made to the files will be automatically committed to the remote.

### What’s its purpose?
gitfs was designed to bring the full powers of git to everyone, irrespective of their experience using the tool. You can mount any repository, and all the changes you make will be automatically converted into commits. gitfs will also expose the history of the branch you’re currently working on by simulating snapshots of every commit.

gitfs is useful in places where you want to keep track of all your files, but at the same time you don’t have the possibility of organizing everything into commits yourself. A FUSE file system for git repositories, with local cache.

### Features
- Automatically commits changes: create, delete, update files and their metadata
- Browse through working index and commit history
- Merges with upstream by automatically accepting local changes
- Mounts the file system as a user or a group
- Caching commits reduces the memory footprint and speeds up navigation
- Reduces the number of commits by grouping pushes

### Development
- You are highly encouraged to use gitfs, to contribute with code, tests, documentation, or just to share your experience. Development of gitfs happens at [github.com/Presslabs/gitfs](https://github.com/Presslabs/gitfs). The concise contribution guide can be found in the [CONTRIBUTING.md](https://github.com/Presslabs/gitfs/blob/master/CONTRIBUTING.md) file.

### License
This project is licensed under the Apache 2.0 license. Have a look at the [LICENSE](https://github.com/Presslabs/gitfs/blob/master/LICENSE) file in the top distribution directory for the complete, unabridged reference.
