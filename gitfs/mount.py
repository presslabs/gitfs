from router import Router
from views import IndexView


router = Router('~/presslabs/testing.git', '/tmp')
router.register(r'^/complete', IndexView)

router.utimens('asdasd', a='asd')
