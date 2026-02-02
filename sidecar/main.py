import asyncio
import logging
import socket
import sys
from contextlib import asynccontextmanager
from typing import cast

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from agents.manager import agent_manager
from core.config import settings
from database.migrations import run_migrations
from database.session import dbsessionmanager
from routers import chat, review, roadmap

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sidecar")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Validate configuration
    if not settings.GEMINI_API_KEY:
        error_msg = (
            "GEMINI_API_KEY is missing. AI features will fail. "
            "Please set it in .env or environment variables."
        )
        logger.critical(error_msg)
        # We raise a RuntimeError to stop startup if the API key is missing
        # This is a strict requirement for the sidecar
        raise RuntimeError(error_msg)

    # Initialize database on startup
    logger.info("Initializing database...")
    await asyncio.to_thread(run_migrations)

    # Initialize agents
    logger.info("Initializing Agent Manager...")
    await agent_manager.initialize_all()

    logger.info("Database and agents initialized. Sidecar is ready.")
    yield
    # Clean up on shutdown
    logger.info("Shutting down...")
    await agent_manager.close_all()
    await dbsessionmanager.close()
    logger.info("Shutdown complete.")


app = FastAPI(title="GeminiSensei Sidecar", lifespan=lifespan)

app.include_router(roadmap.router)
app.include_router(chat.router)
app.include_router(review.router)


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
