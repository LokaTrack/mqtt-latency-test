from ..utils import (
    decrypt_message,
    get_ntp_timestamp,
    create_connection,
    close_connection,
    insert_first_case_data,
    insert_second_case_data,
)
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("uvicorn.error")


async def save_message_published(payload: str):
    """
    Saves the published message payload to a database.

    Args:
        payload (str): The JSON payload of the published message.
    """

    try:
        parsed_payload = decrypt_message(payload)
    except Exception as e:
        logger.debug(f"Error processing payload: {e}")
        return {
            "status": "error",
            "message": f"Failed to process payload: {str(e)}",
            "error_type": type(e).__name__,
        }

    iteration = None
    if isinstance(parsed_payload, dict) and "iteration" in parsed_payload:
        iteration = parsed_payload.get("iteration")

    payload_timestamp_iso = None
    payload_timestamp_epoch = None

    if isinstance(parsed_payload, dict) and "timestamp" in parsed_payload:
        payload_timestamp_datetime = parsed_payload["timestamp"]

        # Convert ISO timestamp to epoch
        try:
            # Parse the ISO timestamp
            dt = datetime.fromisoformat(
                payload_timestamp_datetime.replace("Z", "+00:00")
            )
            payload_timestamp_epoch = dt.timestamp()

            # Update the payload structure
            parsed_payload["timestamp_iso"] = payload_timestamp_datetime
            parsed_payload["timestamp_epoch"] = payload_timestamp_epoch

            # Store for database
            payload_timestamp_iso = payload_timestamp_datetime

            # Remove the original timestamp field
            del parsed_payload["timestamp"]

        except (ValueError, AttributeError) as e:
            logger.debug(
                f"Warning: Could not parse timestamp '{payload_timestamp_datetime}': {e}"
            )
            # Keep original timestamp if parsing fails
            parsed_payload["timestamp_iso"] = payload_timestamp_datetime
            parsed_payload["timestamp_epoch"] = None
            payload_timestamp_iso = payload_timestamp_datetime

    server_timestamp_iso = None
    server_timestamp_epoch = None

    try:
        server_timestamp_epoch = await get_ntp_timestamp()
        server_timestamp_datetime = datetime.fromtimestamp(
            server_timestamp_epoch, tz=timezone.utc
        )
        server_timestamp_iso = server_timestamp_datetime.isoformat()
    except Exception as e:
        logger.debug(f"Warning: Failed to get NTP timestamp: {e}")

    difference = None
    if server_timestamp_epoch is not None and payload_timestamp_epoch is not None:
        difference = server_timestamp_epoch - payload_timestamp_epoch

    database_saved = False
    try:
        conn = create_connection()
        if conn:
            database_saved = insert_first_case_data(
                conn=conn,
                iteration=iteration,
                payload_timestamp_iso=payload_timestamp_iso,
                payload_timestamp_epoch=payload_timestamp_epoch,
                server_timestamp_iso=server_timestamp_iso,
                server_timestamp_epoch=server_timestamp_epoch,
                difference=difference,
            )
            close_connection(conn)
    except Exception as e:
        logger.debug(f"Error saving to database: {e}")

    server_timestamp_data = {
        "timestamp_iso": server_timestamp_iso,
        "timestamp_epoch": server_timestamp_epoch,
    }

    response = {
        "status": "success",
        "message": "Message payload processed successfully",
        "payload": parsed_payload,
        "server": server_timestamp_data,
        "database_saved": database_saved,
        "latency_data": {
            "iteration": iteration,
            "payload_timestamp_iso": payload_timestamp_iso,
            "payload_timestamp_epoch": payload_timestamp_epoch,
            "server_timestamp_iso": server_timestamp_iso,
            "server_timestamp_epoch": server_timestamp_epoch,
            "difference_seconds": difference,
        },
    }

    return response


async def save_message_subscribed(payload: str):
    """
    Saves the subscribed message payload to a database.
    Args:
        payload (str): The JSON payload of the subscribed message.
    """

    try:
        parsed_payload = decrypt_message(payload)
    except Exception as e:
        logger.debug(f"Error processing payload: {e}")
        return {
            "status": "error",
            "message": f"Failed to process payload: {str(e)}",
            "error_type": type(e).__name__,
        }

    iteration = None
    if isinstance(parsed_payload, dict) and "iteration" in parsed_payload:
        iteration = parsed_payload.get("iteration")

    payload_timestamp_iso = None
    payload_timestamp_epoch = None

    if isinstance(parsed_payload, dict) and "timestamp" in parsed_payload:
        payload_timestamp_datetime = parsed_payload["timestamp"]

        # Convert ISO timestamp to epoch
        try:
            # Parse the ISO timestamp
            dt = datetime.fromisoformat(
                payload_timestamp_datetime.replace("Z", "+00:00")
            )
            payload_timestamp_epoch = dt.timestamp()

            # Update the payload structure
            parsed_payload["timestamp_iso"] = payload_timestamp_datetime
            parsed_payload["timestamp_epoch"] = payload_timestamp_epoch

            # Store for database
            payload_timestamp_iso = payload_timestamp_datetime

            # Remove the original timestamp field
            del parsed_payload["timestamp"]

        except (ValueError, AttributeError) as e:
            logger.debug(
                f"Warning: Could not parse timestamp '{payload_timestamp_datetime}': {e}"
            )
            # Keep original timestamp if parsing fails
            parsed_payload["timestamp_iso"] = payload_timestamp_datetime
            parsed_payload["timestamp_epoch"] = None
            payload_timestamp_iso = payload_timestamp_datetime

    server_timestamp_iso = None
    server_timestamp_epoch = None

    try:
        server_timestamp_epoch = await get_ntp_timestamp()
        server_timestamp_datetime = datetime.fromtimestamp(
            server_timestamp_epoch, tz=timezone.utc
        )
        server_timestamp_iso = server_timestamp_datetime.isoformat()
    except Exception as e:
        logger.debug(f"Warning: Failed to get NTP timestamp: {e}")

    difference = None
    if server_timestamp_epoch is not None and payload_timestamp_epoch is not None:
        difference = server_timestamp_epoch - payload_timestamp_epoch

    database_saved = False
    try:
        conn = create_connection()
        if conn:
            database_saved = insert_second_case_data(
                conn=conn,
                iteration=iteration,
                server_timestamp_iso=server_timestamp_iso,
                server_timestamp_epoch=server_timestamp_epoch,
            )
            close_connection(conn)
    except Exception as e:
        logger.debug(f"Error saving to database: {e}")

    server_timestamp_data = {
        "timestamp_iso": server_timestamp_iso,
        "timestamp_epoch": server_timestamp_epoch,
    }

    response = {
        "status": "success",
        "message": "Message payload processed successfully",
        "payload": parsed_payload,
        "server": server_timestamp_data,
        "database_saved": database_saved,
        "latency_data": {
            "iteration": iteration,
            "payload_timestamp_iso": payload_timestamp_iso,
            "payload_timestamp_epoch": payload_timestamp_epoch,
            "server_timestamp_iso": server_timestamp_iso,
            "server_timestamp_epoch": server_timestamp_epoch,
            "difference_seconds": difference,
        },
    }

    return response
