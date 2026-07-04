from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AIDevPulseError(Exception):
    """Base class for all app-specific exceptions."""

    code: str = "internal_error"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AIDevPulseError):
    code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ValidationFailedError(AIDevPulseError):
    code = "validation_failed"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class ExternalServiceError(AIDevPulseError):
    """Raised when an upstream API (OpenAI, Anthropic, RSS source) fails after retries."""

    code = "external_service_error"
    status_code = status.HTTP_502_BAD_GATEWAY


def _envelope(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AIDevPulseError)
    async def handle_app_error(request: Request, exc: AIDevPulseError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope("validation_failed", "Request validation failed."),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope("http_error", message),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope("internal_error", "An unexpected error occurred."),
        )
