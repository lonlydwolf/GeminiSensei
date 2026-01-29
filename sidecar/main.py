import logging
import socket
import sys
from contextlib import asynccontextmanager
from typing import cast

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from database.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sidecar")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Initialize database on startup
    logger.info("Initializing database...")
    await init_db()
    yield
    # Clean up on shutdown
    logger.info("Shutting down...")


app = FastAPI(title="GeminiSensei Sidecar", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello from Gemini Sensei Sidecar!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


def get_free_port() -> int:
    """Returns a free port on the local machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        address_info = cast(tuple[str, int], s.getsockname())
        return address_info[1]
    finally:
        s.close()


if __name__ == "__main__":
    # Get a free port assigned by the OS
    port = get_free_port()

    # Crucial: Print the port in a format Rust can easily parse
    # and flush stdout immediately.
    print(f"PORT:{port}")
    _ = sys.stdout.flush()

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
