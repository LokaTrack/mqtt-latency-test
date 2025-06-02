import uvicorn
from .main import app

if __name__ == "__main__":
    uvicorn.run(
        "src.mqtt_latency_test:app", host="0.0.0.0", port=8000, log_level="debug"
    )
