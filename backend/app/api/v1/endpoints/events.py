"""Server-Sent Events endpoints"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.events import event_manager

router = APIRouter()


@router.get("/{task_id}")
async def stream_events(task_id: str):
    """Stream SSE events for a task"""

    # Connect client
    await event_manager.connect(task_id)

    # Return SSE stream
    return StreamingResponse(
        event_manager.stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )