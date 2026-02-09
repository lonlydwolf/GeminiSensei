from typing import Any, cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

# Import the actual exceptions and handlers
from core.exceptions import BaseAppException, ExternalAPIError, QuotaExceededError
from main import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)


# We will use this to test the handlers later
def create_test_app():
    app = FastAPI()

    # Register the handlers
    app.add_exception_handler(RequestValidationError, cast(Any, validation_exception_handler))
    app.add_exception_handler(BaseAppException, cast(Any, app_exception_handler))
    app.add_exception_handler(Exception, cast(Any, generic_exception_handler))

    @app.get("/validation_error")
    def _validation_error(q: int):  # pyright: ignore [reportUnusedFunction]
        return {"q": q}

    @app.get("/external_api_error")
    def _external_api_error():  # pyright: ignore [reportUnusedFunction]
        raise ExternalAPIError("Google API is down")

    @app.get("/quota_exceeded_error")
    def _quota_exceeded_error():  # pyright: ignore [reportUnusedFunction]
        raise QuotaExceededError("Quota exceeded")

    return app


def test_validation_error_structure():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/validation_error?q=invalid")

    assert response.status_code == 422
    data = response.json()

    # Expecting the NEW structure
    assert "code" in data
    assert data["code"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "details" in data


def test_external_api_error_structure():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/external_api_error")

    assert response.status_code == 502
    data = response.json()

    assert data["code"] == "EXTERNAL_API_ERROR"
    assert data["message"] == "Google API is down"


def test_quota_exceeded_error_structure():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/quota_exceeded_error")

    assert response.status_code == 429
    data = response.json()

    assert data["code"] == "QUOTA_EXCEEDED"
    assert data["message"] == "Quota exceeded"
