import pytest
from mock import MagicMock, PropertyMock, patch, call

from gitfs.utils import Repository
from .base import RepositoryBaseTest


"""
TODO (still need to be tested):
    * commit
    * get_blob_data
    * get_blob_size
    * get_git_object
    * get_git_object_type
"""


class TestRepository(RepositoryBaseTest):

    def test_push(self):
        mocked_repo = MagicMock()
        mocked_remote = MagicMock()
        mocked_remote.name = "origin"
        mocked_repo.remotes = [mocked_remote]

        repo = Repository(mocked_repo)
        repo.push("origin", "master")

        mocked_remote.push.assert_called_once_with("refs/heads/master")
