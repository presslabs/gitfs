from mock import MagicMock, patch

from gitfs.views.commit import CommitView


class TestCommitView(object):
    def test_readdir_without_tree_name(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()

        mocked_entry.name = "entry"
        mocked_commit.tree = [mocked_entry]
        mocked_repo.revparse_single.return_value = mocked_commit

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        with patch('gitfs.views.commit.os') as mocked_os:
            mocked_os.path.split.return_value = [None, None]

            dirs = [entry for entry in view.readdir("/path", 0)]
            assert dirs == [".", "..", "entry"]

            mocked_os.path.split.assert_called_once_with("/path")

    def test_readdir_with_tree_name(self):
        mocked_repo = MagicMock()
        mocked_commit = MagicMock()
        mocked_entry = MagicMock()

        mocked_entry.name = "entry"
        mocked_commit.tree = "tree"
        mocked_repo.revparse_single.return_value = mocked_commit
        mocked_repo.get_git_object.return_value = [mocked_entry]

        view = CommitView(repo=mocked_repo, commit_sha1="sha1")
        with patch('gitfs.views.commit.os') as mocked_os:
            mocked_os.path.split.return_value = [None, True]

            dirs = [entry for entry in view.readdir("/path", 0)]
            assert dirs == [".", "..", "entry"]

            mocked_os.path.split.assert_called_once_with("/path")
            mocked_repo.get_git_object.assert_called_once_with("tree", "/path")
