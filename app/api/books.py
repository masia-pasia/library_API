from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.book import (
    BookCreate,
    BookResponse,
    BookStatusUpdate,
)
from app.services import book_service

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    return book_service.create_book(db, book)

@router.get(
    "",
    response_model=list[BookResponse]
)
def get_books(
    db: Session = Depends(get_db)
):
    return book_service.get_books(db)

@router.delete(
    "/{serial_number}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_book(
    serial_number: Annotated[str, Path(pattern=r"^\d{6}$")],
    db: Session = Depends(get_db)
):
    book_service.delete_book(db, serial_number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch(
    "/{serial_number}/status",
    response_model=BookResponse
)
def update_book_status(
    serial_number: Annotated[str, Path(pattern=r"^\d{6}$")],
    status_data: BookStatusUpdate,
    db: Session = Depends(get_db)
):
    return book_service.update_book_status(
        db,
        serial_number,
        status_data
    )