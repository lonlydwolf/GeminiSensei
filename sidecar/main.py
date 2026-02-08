import asyncio
import logging
import socket
import sys
from contextlib import asynccontextmanager
from typing import cast

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.manager import agent_manager
from core.config import settings
from database.migrations import run_migrations
from database.session import dbsessionmanager
from routers import agents, app_settings, chat, review, roadmap

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sidecar")


def validate_config():
    """Validates core configuration. Returns True if valid, False otherwise."""
    if not settings.GEMINI_API_KEY:
        error_msg = (
            "GEMINI_API_KEY is missing. AI features will fail. "
            "Please set it in Settings or environment variables."
        )
        logger.warning(error_msg)
        return False
    return True


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Validate configuration on startup
    _ = validate_config()

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

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roadmap.router)
app.include_router(chat.router)
app.include_router(review.router)
app.include_router(agents.router)
app.include_router(app_settings.router)


@app.get("/")
def read_root():
    return {"message": "Hello from Gemini Sensei Sidecar!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


def bind_random_port() -> tuple[socket.socket, int]:
    """Binds to a random port and returns the socket and port number."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    # Required for the socket to be useful for uvicorn
    sock.listen(5)
    address_info = cast(tuple[str, int], sock.getsockname())
    return sock, address_info[1]


if __name__ == "__main__":
    # Perform pre-flight checks
    _ = validate_config()

    # Get a free port assigned by the OS and keep the socket open
    sock, port = bind_random_port()

    # Crucial: Print the port in a format Rust can easily parse
    # and flush stdout immediately.
    print(f"PORT:{port}")
    _ = sys.stdout.flush()

    # Use the file descriptor of the already bound socket
    config = uvicorn.Config(app, fd=sock.fileno(), log_level="info")
    server = uvicorn.Server(config)

    try:
        asyncio.run(server.serve())
    finally:
        sock.close()
