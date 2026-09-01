import os

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="HT-Run",
    version="1.0.0",
)


class MessageRequest(BaseModel):
    user_id: int
    message: str


class MessageResponse(BaseModel):
    status: str
    user_id: int
    message: str


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ht-run",
    }


@app.post("/message", response_model=MessageResponse)
async def receive_message(request: MessageRequest):
    """
    Receive a message from the Telegram bot.

    Browser automation will be connected here later.
    """
    return MessageResponse(
        status="received",
        user_id=request.user_id,
        message=request.message,
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
    )
