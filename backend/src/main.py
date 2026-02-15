"""FastAPI application bootstrap."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors import (
    Lab2FHIRException,
    general_exception_handler,
    http_exception_handler,
    lab2fhir_exception_handler,
)
from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Lab2FHIR API starting up...")
    yield
    # Shutdown
    print("👋 Lab2FHIR API shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Lab2FHIR API",
        description="Backend API for Lab PDF to FHIR Converter",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(Lab2FHIRException, lab2fhir_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Register routers
    from src.api import bundles, parsed_data, patients, reports

    app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
    app.include_router(parsed_data.router, prefix="/api/v1/parsed-data", tags=["parsed-data"])
    app.include_router(bundles.router, prefix="/api/v1/bundles", tags=["bundles"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "lab2fhir-api"}

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
