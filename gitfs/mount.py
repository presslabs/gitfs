from router import Router
from views import IndexView


router = Router('~/presslabs/testing.git', '/tmp')
router.register(r'^/complete/relativity/is/good/(?P<path>\w+)/(\w+)',
                IndexView)

router.open('/cpmplete/relativity/is/good/one/two/three/four/five.six', 'arg')
