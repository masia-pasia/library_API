import logging

from fastapi import FastAPI, Request

from app.api.books import router as books_router


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Library API",
    description="API for managing library books",
    version="1.0.0",
)


@app.middleware("http")
async def log_failed_requests(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error: %s %s",
            request.method,
            request.url.path,
        )
        raise

    if response.status_code >= 400:
        logger.warning(
            "Request failed: %s %s returned %d",
            request.method,
            request.url.path,
            response.status_code,
        )

    return response


app.include_router(books_router)