from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import message_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the MQTT Latency Test API!"}
