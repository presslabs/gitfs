import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from router import Router
from views import IndexView, CurrentView, HistoryIndexView, HistoryView

mount_path = '/tmp/gitfs/mnt'

router = Router(remote_url='/home/zalman/dev/presslabs/test-repo.git',
                repos_path='/tmp/gitfs/repos/',
                mount_path=mount_path)

# TODO: replace regex with the strict one for the Historyview
# -> r'^/history/(?<date>(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01]))/',
router.register(r'^/history/(?P<date>\d{4}-\d{1,2}-\d{1,2})/(?P<time>\d{2}:\d{2}:\d{2})-(?P<commit_sha1>[0-9a-f]{10})', HistoryView)
router.register(r'^/history/(?P<date>\d{4}-\d{1,2}-\d{1,2})', HistoryIndexView)
router.register(r'^/history', HistoryIndexView)
router.register(r'^/current', CurrentView)
router.register(r'^/', IndexView)

from fuse import FUSE
FUSE(router, mount_path, foreground=True, nonempty=True)
