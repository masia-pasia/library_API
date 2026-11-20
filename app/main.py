from fastapi import FastAPI

from app.api.books import router as books_router


app = FastAPI(
    title="Library API",
    description="API for managing library books",
    version="1.0.0",
)

app.include_router(books_router)