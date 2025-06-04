import uvicorn
import os
from dotenv import load_dotenv
from .main import app

load_dotenv()  # Add parentheses to actually call the function

if __name__ == "__main__":
    log_level = os.getenv("DEBUG_LEVEL", "info").strip().lower()
    if not log_level or log_level not in [
        "critical",
        "error",
        "warning",
        "info",
        "debug",
        "trace",
    ]:
        log_level = "info"

    uvicorn.run(
        "src.mqtt_latency_test:app",
        host="0.0.0.0",
        port=8001,
        log_level=log_level,
    )
