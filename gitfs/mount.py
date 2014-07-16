from .router import Router
from .views import IndexView


router = Router()
router.register(r'^/complete', IndexView)
