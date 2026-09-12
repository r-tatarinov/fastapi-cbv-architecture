from fastapi import FastAPI

from src.app.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title=__PROJECT_NAME_LITERAL__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.include_router(router)
    return app


application: FastAPI = create_app()

__all__ = ["application", "create_app"]
