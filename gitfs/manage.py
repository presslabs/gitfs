import click
from fuse import FUSE

from gitfs.filesystems.git_fuse import GitFuse


@click.command()
@click.argument("remote-url")
@click.argument("mount-point")
@click.option("--repos-path", default="/tmp",
              help="A path representing where to keep cloned repos")
@click.option("--branch", default=None,
              help="Specific which branch to follow. The default is to use " +
              "the remote's default branch.")
@click.option("--foreground", default=True, type=bool,
              help="Start in foreground or not")
def run(remote_url, mount_point, repos_path, foreground, branch):
    """Mount a remote repository to a local mount point"""
    fs = GitFuse(remote_url, repos_path, branch)

    FUSE(fs, mount_point, foreground=foreground)
