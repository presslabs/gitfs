from router import Router
from views import IndexView

mount_path = '/tmp/gitfs/mnt'

router = Router('/home/zalman/dev/presslabs/test-repo.git', '/tmp/gitfs/repos/')

#router.register(r'^/complete/relativity/is/good/(?P<path>\w+)/(\w+)',
                #IndexView)

#router.open('/complete/relativity/is/good/one/two/three/four/five.six', 'arg')
router.register(r'^/', IndexView)

from fuse import FUSE
FUSE(router, mount_path, foreground=True, nonempty=True)
