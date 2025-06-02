from fastapi import APIRouter, Request
from ..handlers import save_message_published, save_message_subscribed
from ..utils import (
    ntp_sync,
    get_ntp_timestamp,
    get_ntp_datetime,
    create_connection,
    close_connection,
)
import json
import sqlite3
import logging

logger = logging.getLogger("uvicorn.error")

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
        logger.debug(f"Error processing request: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/subscribe")
async def message_subscribed(request: Request):
    try:
        data = await request.json()

        payload = data.get("payload")
        if not payload:
            return {"status": "error", "message": "No payload found in request data"}

        result = await save_message_subscribed(payload)
        return result
    except Exception as e:
        logger.debug(f"Error processing request: {e}")
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


@router.get("/data")
async def get_latency_data():
    """
    Get all latency test data from the first_case table.
    """
    try:
        conn = create_connection()
        if not conn:
            return {"status": "error", "message": "Failed to connect to database"}

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, iteration, payload_timestamp_iso, payload_timestamp_epoch, 
                   server_timestamp_iso, server_timestamp_epoch, difference, created_at
            FROM first_case 
            ORDER BY created_at DESC
        """
        )

        rows = cursor.fetchall()
        close_connection(conn)

        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(
                {
                    "id": row[0],
                    "iteration": row[1],
                    "payload_timestamp_iso": row[2],
                    "payload_timestamp_epoch": row[3],
                    "server_timestamp_iso": row[4],
                    "server_timestamp_epoch": row[5],
                    "difference_seconds": row[6],
                    "created_at": row[7],
                }
            )

        return {
            "status": "success",
            "message": f"Retrieved {len(data)} records",
            "data": data,
        }

    except Exception as e:
        logger.debug(f"Error retrieving data: {e}")
        return {"status": "error", "message": str(e)}
