import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from router import Router
from views import IndexView
from views import CurrentView

mount_path = '/tmp/gitfs/mnt'

router = Router(remote_url='/home/zalman/dev/presslabs/test-repo.git',
                repos_path='/tmp/gitfs/repos/',
                mount_path=mount_path)

#router.register(r'^/complete/relativity/is/good/(?P<path>\w+)/(\w+)',
                #IndexView)

#router.open('/complete/relativity/is/good/one/two/three/four/five.six', 'arg')
router.register(r'^/current', CurrentView)
router.register(r'^/', IndexView)

from fuse import FUSE
FUSE(router, mount_path, foreground=True, nonempty=True)
