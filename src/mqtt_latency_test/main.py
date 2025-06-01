from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import message_router
from .utils import ntp_sync
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(message_router)


async def background_ntp_sync():
    """
    Background task to keep NTP synchronized.
    Syncs every 25 seconds to ensure cache stays fresh (cache duration is 30s).
    """
    while True:
        try:
            await ntp_sync.get_ntp_timestamp()  # This will sync if needed
        except Exception as e:
            print(f"Background NTP sync failed: {e}")

        # Wait 25 seconds before next sync (less than 30s cache duration)
        await asyncio.sleep(25)


@app.on_event("startup")
async def startup_event():
    """
    Perform initial NTP synchronization on server startup.
    """
    try:
        # Perform initial NTP sync
        await ntp_sync.get_ntp_timestamp()

        # Start background sync task
        asyncio.create_task(background_ntp_sync())

    except Exception as e:
        print(f"Startup NTP sync failed: {e}")


@app.get("/")
async def root():
    return {"message": "Welcome to the MQTT Latency Test API!"}
