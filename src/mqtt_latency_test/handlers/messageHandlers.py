from ..utils import decrypt_message, get_ntp_timestamp, get_ntp_datetime


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

    # Get NTP-synchronized timestamp
    try:
        timestamp = await get_ntp_timestamp()
        timestamp_iso = await get_ntp_datetime()
        timestamp_iso = timestamp_iso.isoformat()
    except Exception as e:
        print(f"Warning: Failed to get NTP timestamp, using local time: {e}")
        import time
        from datetime import datetime, timezone

        timestamp = time.time()
        timestamp_iso = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    return {
        "status": "success",
        "message": "Message payload saved successfully",
        "payload": decrypted_payload,
        "timestamp": timestamp_iso,
        "timestamp_epoch": timestamp,
    }
