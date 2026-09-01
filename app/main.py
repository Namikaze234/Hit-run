from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="HT-Run API",
    version="1.0.0",
)


class MessageRequest(BaseModel):
    user_id: int
    message: str


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ht-run-api",
    }


@app.post("/message")
async def receive_message(request: MessageRequest):
    return {
        "status": "received",
        "user_id": request.user_id,
        "message": request.message,
    }
