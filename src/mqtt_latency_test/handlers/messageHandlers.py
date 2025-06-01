from ..utils import decrypt_message, get_ntp_timestamp, get_ntp_datetime
import json
from datetime import datetime


async def save_message_published(payload: str):
    """
    Saves the published message payload to a file.

    Args:
        payload (str): The JSON payload of the published message.
    """

    try:
        decrypted_payload = decrypt_message(payload)

    except Exception as e:
        print(f"Error decrypting message: {e}")
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

    # Parse the decrypted payload if it's a JSON string
    try:
        if isinstance(decrypted_payload, str):
            parsed_payload = json.loads(decrypted_payload)
        else:
            parsed_payload = decrypted_payload
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON payload: {e}")
        return {
            "status": "error",
            "message": "Failed to parse payload as JSON",
            "error": str(e),
        }

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

            # Remove the original timestamp field
            del parsed_payload["timestamp"]

        except (ValueError, AttributeError) as e:
            print(
                f"Warning: Could not parse timestamp '{payload_timestamp_datetime}': {e}"
            )
            # Keep original timestamp if parsing fails
            parsed_payload["timestamp_iso"] = payload_timestamp_datetime
            parsed_payload["timestamp_epoch"] = None

    # Get NTP-synchronized timestamp
    try:
        server_timestamp_epoch = await get_ntp_timestamp()
        server_timestamp_datetime = await get_ntp_datetime()
        server_timestamp_iso = server_timestamp_datetime.isoformat()
    except Exception as e:
        print(f"Warning: Failed to get NTP timestamp, using local time: {e}")
        import time
        from datetime import timezone

        server_timestamp_epoch = time.time()
        server_timestamp_iso = datetime.fromtimestamp(
            server_timestamp_epoch, tz=timezone.utc
        ).isoformat()

    # Create timestamp object
    server_timestamp_data = {
        "timestamp_iso": server_timestamp_iso,
        "timestamp_epoch": server_timestamp_epoch,
    }

    # Create response object
    response = {
        "status": "success",
        "message": "Message payload saved successfully",
        "payload": parsed_payload,
        "server": server_timestamp_data,
    }

    print(f"Response: {json.dumps(response, indent=2)}")

    return response
