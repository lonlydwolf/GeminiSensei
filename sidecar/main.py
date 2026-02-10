import asyncio
import logging
import secrets
import socket
import sys
from contextlib import asynccontextmanager
from typing import Annotated, cast

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agents.manager import agent_manager
from core.config import settings
from core.exceptions import BaseAppException, ExternalAPIError, QuotaExceededError
from database.migrations import run_migrations
from database.session import dbsessionmanager
from routers import agents, app_settings, chat, review, roadmap

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sidecar")

# Generate a single-session token for authentication
SIDECAR_SECRET = secrets.token_urlsafe(32)


async def verify_sidecar_token(x_sidecar_token: Annotated[str | None, Header()] = None):
    """Verifies the sidecar token provided in headers."""
    if x_sidecar_token != SIDECAR_SECRET:
        logger.warning(f"Unauthorized access attempt with token: {x_sidecar_token}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid sidecar token")
    return x_sidecar_token


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
    config_valid = validate_config()

    # Initialize database on startup (always needed)
    logger.info("Initializing database...")
    await asyncio.to_thread(run_migrations)

    # Initialize agents ONLY if API key is configured
    if config_valid and settings.GEMINI_API_KEY:
        logger.info("Initializing Agent Manager...")
        try:
            await agent_manager.initialize_all()
            logger.info("Agents initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            logger.warning("Agents will remain uninitialized. Set API key to enable AI features.")
    else:
        logger.warning("Skipping agent initialization - API key not configured.")
        logger.info("Please configure API key through the Welcome screen to enable AI features.")

    # Log initial stats
    try:
        from sqlalchemy import func, select

        from database.models import Roadmap

        async with dbsessionmanager.session() as db:
            result = await db.execute(select(func.count(Roadmap.id)))
            count = result.scalar()
            logger.info(f"Database connected. Found {count} roadmap(s).")
    except Exception as e:
        logger.warning(f"Could not fetch roadmap count: {e}")

    logger.info("Database initialized. Sidecar is ready.")
    yield
    # Clean up on shutdown
    logger.info("Shutting down...")
    await agent_manager.close_all()
    await dbsessionmanager.close()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="GeminiSensei Sidecar",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": {"errors": exc.errors()},
        },
    )


@app.exception_handler(BaseAppException)
async def app_exception_handler(_request: Request, exc: BaseAppException):
    status_code = 500
    if isinstance(exc, QuotaExceededError):
        status_code = 429
    elif isinstance(exc, ExternalAPIError):
        status_code = 502

    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "details": {"error": str(exc)},
        },
    )


# Add CORS Middleware
origins = [
    "*",  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Credentials not needed for token auth
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "X-Sidecar-Token"],
)

# API Router with Authentication
api_router = APIRouter(dependencies=[Depends(verify_sidecar_token)])

api_router.include_router(roadmap.router)
api_router.include_router(chat.router)
api_router.include_router(review.router)
api_router.include_router(agents.router)
api_router.include_router(app_settings.router)

app.include_router(api_router)


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

    # Crucial: Print the port and token in a format Rust can easily parse
    # and flush stdout immediately.
    print(f"PORT:{port}")
    _ = sys.stdout.flush()
    print(f"TOKEN:{SIDECAR_SECRET}")
    _ = sys.stdout.flush()

    # Use the file descriptor of the already bound socket
    config = uvicorn.Config(app, fd=sock.fileno(), log_level="info")
    server = uvicorn.Server(config)

    try:
        asyncio.run(server.serve())
    finally:
        sock.close()
