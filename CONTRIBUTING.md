# Contributing

We love pull requests. Here's a quick guide.

Fork, then clone the repo:
```
git clone git@github.com:your-username/gitfs.git
```

Start a Vagrant box
```
vagrant up
```

Make your changes, write the tests and then:
```
make clean
make test
```

Push to your fork and submit the pull request.

## Mounting for development

In order to mount for development, you should mount with `foreground` and
`debug` set to `true` and `log` set to `/dev/stderr`:

```
mount.fuse gitfs#http://github.com/vtemian/testing.git /tmp/mnt -o repo_path="/tmp/git-test",foreground=true,debug=true,log=/dev/stderr
```

## Code style

The code should be properly formatted acording to PEP8, using 4 spaces
