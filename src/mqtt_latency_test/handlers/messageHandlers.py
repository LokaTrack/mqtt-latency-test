from ..utils import decrypt_message


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

    return {
        "status": "success",
        "message": "Message payload saved successfully",
        "payload": decrypted_payload,
    }
