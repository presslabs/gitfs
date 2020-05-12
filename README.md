gitfs [![Build Status](https://drone.presslabs.net/api/badges/PressLabs/gitfs/status.svg?arrra)](https://drone.presslabs.net/github.com/PressLabs/gitfs) [![Coverage Status](https://coveralls.io/repos/PressLabs/gitfs/badge.png?branch=HEAD)](https://coveralls.io/r/PressLabs/gitfs?branch=HEAD) ![PyPI](https://img.shields.io/pypi/v/gitfs)
========

# Welcome to GitFS

gitfs is a [FUSE](http://fuse.sourceforge.net/) file system that fully
integrates with git. You can mount a remote repository's branch locally, and any
subsequent changes made to the files will be automatically committed to the
remote.

gitfs was developed by the awesome engineering team at [Presslabs](https://www.presslabs.com/),
a Managed WordPress Hosting provider.

## What's its purpose?

gitfs was designed to bring the full powers of git to everyone, no matter how
little they know about versioning. A user can mount any repository and all their 
changes will be automatically converted into commits. gitfs will also expose
the history of the branch you're currently working on by simulating snapshots of
every commit.

gitfs is useful in places where you want to keep track of all your files, but at
the same time you don't have the possibility of organizing everything into
commits yourself. A FUSE filesystem for git repositories, with local cache.

## Installing

We provide packages for the major Ubuntu releases and MacOS, but you can find community packages for most of popular Linux
distributions. If you want to build packages for a distribution, or you already did, please contact us and we'll list it here.

### Ubuntu 18.04+

```bash
sudo add-apt-repository ppa:presslabs/gitfs
sudo apt-get update
sudo apt-get install gitfs
```

### MacOS

```bash
brew install gitfs
```

#### Pip

We also publish a package to PyPI, which can be installed via pip using the following commmand:

```bash
pip install gitfs
```

## Usage

You can mount a remote or local repository easly, just by providing the repository to clone and a directory used to mount.

```bash
gitfs http://your.com/repository.git /mount/directory
```

The entire filesystem can be tweaked when mounting it, using a set of options.

```bash
gitfs git@github.com:user/repo.git /mypath -o
repo_path=/tmp/path,branch=dev,log=-,debug=true,foreground=true,fetch_timeout=0.1,merge_timeout=0.1...
```

For an entire list of options, you can check the [arguments page](https://www.presslabs.com/code/gitfs/arguments/).

## Features
* Automatically commits changes: create, delete, update files and their metadata
* Browse through working index and commit history
* Merges with upstream by automatically accepting local changes
* Caching commits reduces the memory footprint and speeds up navigation
* Reduces the number of pushes by batching commits

## Development

You can find more documentation on [gitfs homepage](https://www.presslabs.com/code/gitfs/).

### Contributing

Development of gitfs happens at http://github.com/presslabs/gitfs.

Issues are tracked at http://github.com/presslabs/gitfs/issues.

The Python package can be found at https://pypi.python.org/pypi/gitfs/.

You are highly encouraged to contribute with code, tests, documentation or just
sharing experience.

Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License
This project is licensed under Apache 2.0 license. Read the [LICENSE](LICENSE) file in the
top distribution directory for the full license text.
