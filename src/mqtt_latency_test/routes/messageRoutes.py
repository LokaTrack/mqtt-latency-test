from fastapi import APIRouter, Request
from ..handlers import save_message_published
import json

router = APIRouter(prefix="/message", tags=["message"])


@router.post("/publish")
async def message_published(request: Request):
    try:
        data = await request.json()
        # print("Received JSON data:")
        # print(json.dumps(data, indent=2))

        payload = data.get("payload")
        if not payload:
            return {"status": "error", "message": "No payload found in request data"}

        result = await save_message_published(payload)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"status": "error", "message": str(e)}
