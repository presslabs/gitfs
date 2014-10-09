# Welcome to GitFS

gitfs is a [FUSE](http://fuse.sourceforge.net/) file system that fully integrates with git. You can mount a remote repository's branch locally, and any subsequent changes made to the files will be automatically committed to the remote.

## What's its purpose?

gitfs was designed to bring the full powers of git to everyone, no matter how little they know about versioning. A user can mount any repository and all the his changes will be automatically converted into commits. gitfs will also expose the history of the branch you're currently working on by simulating snapshots of every commit.

gitfs is useful in places where you want to keep track of all your files, but at the same time you don't have the possibility of organizing everything into commits yourself.
