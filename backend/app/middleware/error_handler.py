"""Middleware for error handling."""

import json
import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Custom error handler middleware.
    Catches exceptions and returns formatted JSON responses.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request and handle any exceptions.
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response or error response
        """
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "detail": str(e),
                    "error_code": "VALIDATION_ERROR",
                },
            )
        except Exception as e:
            logger.exception(f"Unhandled error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                },
            )
