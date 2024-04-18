import fastapi

from src.utilities.messages.exceptions.http.exc_details import http_412_task_not_complete_details


async def http_412_exc_task_not_complete_request(task_id: int) -> Exception:
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_412_PRECONDITION_FAILED,
        detail=http_412_task_not_complete_details(task_id=task_id),
    )