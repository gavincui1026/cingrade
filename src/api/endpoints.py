import fastapi

from src.api.routes.account import router as account_router
from src.api.routes.miner import router as miner_router
from src.api.routes.authentication import router as auth_router
from src.api.routes.wallet import router as wallet_router
from src.api.routes.movie import router as movie_router
from src.api.routes.oss import router as oss_router
from src.api.routes.task import router as task_router
from src.api.admin import router as admin_router
router = fastapi.APIRouter()

router.include_router(router=account_router)
router.include_router(router=auth_router)
router.include_router(router=miner_router)
router.include_router(router=wallet_router)
router.include_router(router=movie_router)
router.include_router(router=oss_router)
router.include_router(router=task_router)
router.include_router(router=admin_router)