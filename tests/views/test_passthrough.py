import pytest
from mock import patch

from fuse import FuseOSError

from gitfs.views.passthrough import PassthroughView


class TestPassthrodugh(object):
    def test_full_path(self):
        with patch('gitfs.views.passthrough.os') as mocked_os:
            mocked_os.path.join.return_value = "simple_path"

            pass_view = PassthroughView(repo_path="/root")

            assert pass_view._full_path("/repo") == "simple_path"
            mocked_os.path.join.asserted_called_once_with("/root", "repo")

    def test_access(self):
         with patch('gitfs.views.passthrough.os') as mocked_os:
             mocked_os.access.return_value = False

             pass_view = PassthroughView(repo_path="/root")

             with pytest.raises(FuseOSError):
                 pass_view.access("path", "mode")

             mocked_os.access.asserted_called_once_with("/root/path", "mode")
