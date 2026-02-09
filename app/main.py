"""
Production-ready stateless REST API for Kubernetes
Built with FastAPI - suitable for cloud-native deployments
"""

import os
import socket
from typing import Dict

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn

# ============================================================================
# Configuration from environment variables with sensible defaults
# ============================================================================

APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
PORT = int(os.getenv("PORT", "8080"))

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Kubernetes Production API",
    description="Stateless REST API with health checks and metrics",
    version=APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
)

# ============================================================================
# Prometheus Metrics
# ============================================================================

# Counter for total HTTP requests
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# Histogram for request duration
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

# ============================================================================
# Middleware for automatic metrics collection
# ============================================================================

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Middleware to automatically track request metrics
    Records duration and counts for all HTTP requests
    """
    method = request.method
    path = request.url.path
    
    # Measure request duration
    with http_request_duration_seconds.labels(method=method, endpoint=path).time():
        response = await call_next(request)
    
    # Count requests by status code
    http_requests_total.labels(
        method=method,
        endpoint=path,
        status=response.status_code
    ).inc()
    
    return response

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint - returns runtime information
    
    Returns:
        Dict with environment, version, and hostname information
    """
    return {
        "environment": APP_ENV,
        "version": APP_VERSION,
        "hostname": socket.gethostname(),  # Returns pod name in Kubernetes
        "message": "Kubernetes Production API - Running"
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Health check endpoint for Kubernetes liveness probe
    
    Returns:
        Simple status indicator - fast response for K8s health checks
    """
    return {"status": "ok"}


@app.get("/readiness")
async def readiness() -> Dict[str, str]:
    """
    Readiness check endpoint for Kubernetes readiness probe
    
    In a real application, this would check:
    - Database connectivity
    - External service dependencies
    - Cache availability
    
    Returns:
        Simple ready indicator
    """
    # Add actual dependency checks here in production
    # For now, always ready since we're stateless
    return {"status": "ready"}


@app.get("/metrics")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint
    
    Exposes metrics in Prometheus format for scraping
    Kubernetes can scrape this endpoint for monitoring
    
    Returns:
        Prometheus-formatted metrics
    """
    metrics_output = generate_latest()
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )

# ============================================================================
# Application Startup
# ============================================================================

if __name__ == "__main__":
    """
    Start the application server
    
    Configuration:
    - Host: 0.0.0.0 (accepts connections from any interface - required for K8s)
    - Port: 8080 (configurable via PORT env var)
    - Workers: 1 (Kubernetes handles horizontal scaling)
    - Log level: Configurable via LOG_LEVEL env var
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
    )
