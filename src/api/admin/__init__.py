import fastapi


from src.api.admin.referer import router as referer_router
from src.api.admin.task import router as task_router
from src.api.admin.referer import router as referer_router

router = fastapi.APIRouter(prefix="/admin", tags=["admin"])


router.include_router(router=referer_router)
router.include_router(router=task_router)