from ..utils import (
    decrypt_message,
    get_ntp_timestamp,
    get_ntp_datetime,
    create_connection,
    close_connection,
    insert_first_case_data,
)
import json
import logging
from datetime import datetime

logger = logging.getLogger("uvicorn.error")


async def save_message_published(payload: str):
    """
    Saves the published message payload to a database.

    Args:
        payload (str): The JSON payload of the published message.
    """

    try:
        decrypted_payload = decrypt_message(payload)

    except Exception as e:
        logger.debug(f"Error decrypting message: {e}")
        return {
            "status": "error",
            "message": "Failed to decrypt message payload",
            "error": str(e),
        }

    if decrypted_payload is None:
        return {
            "status": "error",
            "message": "Decrypted payload is None",
        }

    try:
        if isinstance(decrypted_payload, str):
            parsed_payload = json.loads(decrypted_payload)
        else:
            parsed_payload = decrypted_payload

    except json.JSONDecodeError as e:
        logger.debug(f"Error parsing JSON payload: {e}")
        return {
            "status": "error",
            "message": "Failed to parse payload as JSON",
            "error": str(e),
        }

    # Extract iteration field
    iteration = None
    if isinstance(parsed_payload, dict) and "iteration" in parsed_payload:
        iteration = parsed_payload.get("iteration")

    # Initialize timestamp variables
    payload_timestamp_iso = None
    payload_timestamp_epoch = None

    # Transform timestamp field if it exists
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

    # Get NTP-synchronized timestamp
    server_timestamp_iso = None
    server_timestamp_epoch = None

    try:
        server_timestamp_epoch = await get_ntp_timestamp()
        server_timestamp_datetime = await get_ntp_datetime()
        server_timestamp_iso = server_timestamp_datetime.isoformat()

    except Exception as e:
        logger.debug(f"Warning: Failed to get NTP timestamp: {e}")

    # Calculate time difference (server - payload)
    difference = None
    if server_timestamp_epoch is not None and payload_timestamp_epoch is not None:
        difference = server_timestamp_epoch - payload_timestamp_epoch

    server_timestamp_data = {
        "timestamp_iso": server_timestamp_iso,
        "timestamp_epoch": server_timestamp_epoch,
    }

    # Save to database
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

    # Create response object
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

    logger.debug(f"Response: {json.dumps(response, indent=2)}")

    return response
