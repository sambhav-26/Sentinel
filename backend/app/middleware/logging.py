"""Middleware for request/response logging."""

import json
import logging
import time
from typing import Callable

from fastapi import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """
    Custom logging middleware.
    Logs all requests and responses with timing information.
    """

    def __init__(self, app):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
        """
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        """
        Process request and log timing.
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response with logged details
        """
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"(took {process_time:.3f}s)"
        )

        return response
