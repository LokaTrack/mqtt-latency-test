from fastapi import APIRouter, Request
from ..handlers import save_message_published
from ..utils import ntp_sync, get_ntp_timestamp, get_ntp_datetime
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


@router.get("/ntp-status")
async def get_ntp_status():
    """
    Get NTP synchronization status and current NTP time.
    Useful for debugging and monitoring NTP sync health.
    """
    try:
        cache_status = ntp_sync.get_cache_status()

        # Only get current timestamps if we have synced at least once
        if cache_status["status"] != "not_synced":
            current_timestamp = await get_ntp_timestamp()
            current_datetime = await get_ntp_datetime()

            return {
                "status": "success",
                "ntp_cache": cache_status,
                "current_timestamp": current_timestamp,
                "current_datetime": current_datetime.isoformat(),
                "server": ntp_sync.ntp_server,
            }
        else:
            # If not synced, try to sync now and return the result
            try:
                current_timestamp = await get_ntp_timestamp()  # This will trigger sync
                current_datetime = await get_ntp_datetime()
                updated_cache_status = ntp_sync.get_cache_status()

                return {
                    "status": "success",
                    "ntp_cache": updated_cache_status,
                    "current_timestamp": current_timestamp,
                    "current_datetime": current_datetime.isoformat(),
                    "server": ntp_sync.ntp_server,
                    "note": "Performed fresh sync as no previous sync was available",
                }
            except Exception as sync_error:
                return {
                    "status": "error",
                    "ntp_cache": cache_status,
                    "message": f"Not synced and failed to sync now: {str(sync_error)}",
                    "server": ntp_sync.ntp_server,
                }

    except Exception as e:
        return {"status": "error", "message": f"Failed to get NTP status: {str(e)}"}
