from mock import patch

from gitfs.views.passthrough import PassthroughView


class TestPassthrodugh(object):
    def test_full_path(self):
        with patch('gitfs.views.passthrough.os') as mocked_os:
            mocked_os.path.join.return_value = "simple_path"

        pass_view = PassthroughView(repo_path="/root")

        assert pass_view._full_path("/repo") == "/root/repo"
        mocked_os.path.join.asserted_called_once_with("/root", "repo")
