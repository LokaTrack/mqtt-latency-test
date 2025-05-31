from fastapi import APIRouter, Request
import json

router = APIRouter(prefix="/message", tags=["message"])


@router.post("/publish")
async def message_published(request: Request):
    try:
        data = await request.json()
        print("Received JSON data:")
        print(json.dumps(data, indent=2))
        return {"status": "success", "message": "Message published successfully"}
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"status": "error", "message": e.__str__()}
