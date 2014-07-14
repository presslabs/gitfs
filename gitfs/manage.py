import click
from fuse import FUSE

from gitfs.filesystems import GitFuse


@click.command()
@click.argument("remote-url")
@click.argument("mount-point")
@click.option("--repos-path", default="/tmp",
              help="A path representing where to keep cloned repos")
@click.option("--foreground", default=True, type=bool,
              help="Start in foreground or not")
def run(remote_url, mount_point, repos_path, foreground):
  """Mount a remote repository to a local mount point"""
  fs = GitFuse(remote_url, repos_path)

  FUSE(fs, mount_point, foreground=foreground)
