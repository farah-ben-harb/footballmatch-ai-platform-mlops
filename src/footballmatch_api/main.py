from fastapi import FastAPI

from footballmatch_api.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health")
def health() -> dict[str, str]:
    """Return basic process health."""

    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Return readiness for serving traffic."""

    return {"status": "ready", "environment": settings.environment}
