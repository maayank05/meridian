"""FastAPI app factory: versioned routes, error envelope, request IDs, structured logs, narrow CORS.

Run locally: uvicorn meridian.api.main:app --reload   (reads the database with the READ-ONLY account)
"""

import json
import logging
import os
import time
import uuid
from collections.abc import Callable
from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from meridian.api.routes import router
from meridian.db import Role, make_engine

log = logging.getLogger("meridian.api")


@lru_cache
def reader_engine() -> Engine:
    return make_engine(Role.READER)


def _envelope(status: int, code: str, message: str, request: Request, details=None) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "request_id": getattr(request.state, "request_id", None)}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def create_app(engine_factory: Callable[[], Engine] = reader_engine) -> FastAPI:
    app = FastAPI(
        title="MERIDIAN API",
        version="1.0.0",
        description="Decision intelligence for the simulated Northstar Commerce (Olist data, CC BY-NC-SA 4.0).",
    )
    app.state.engine_factory = engine_factory
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = rid[:64]
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        log.info(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                }
            )
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return _envelope(422, "validation_error", "Invalid request parameters", request, details)

    @app.exception_handler(ValueError)
    async def domain_error(request: Request, exc: ValueError):
        return _envelope(422, "invalid_input", str(exc), request)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return _envelope(exc.status_code, "http_error", str(exc.detail), request)

    @app.exception_handler(OperationalError)
    async def db_unavailable(request: Request, exc: OperationalError):
        log.error(json.dumps({"request_id": request.state.request_id, "error": "database_unavailable"}))
        return _envelope(503, "database_unavailable", "The analytics database is not reachable", request)

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        log.error(json.dumps({"request_id": request.state.request_id, "error": type(exc).__name__}))
        return _envelope(500, "internal_error", "Unexpected server error", request)

    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
