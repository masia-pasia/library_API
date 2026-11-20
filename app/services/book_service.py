
import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookStatusUpdate


logger = logging.getLogger(__name__)


def create_book(db: Session, book_data: BookCreate) -> Book:
    existing_book = db.scalar(
        select(Book).where(
            Book.serial_number == book_data.serial_number
        )
    )

    if existing_book:
        raise HTTPException(
            status_code=409,
            detail="Book with this serial number already exists"
        )

    book = Book(
        serial_number=book_data.serial_number,
        title=book_data.title,
        author=book_data.author,
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    logger.info("Book %s created", book.serial_number)

    return book


def get_books(db: Session) -> list[Book]:
    return list(
        db.scalars(
            select(Book)
        ).all()
    )


def delete_book(db: Session, serial_number: str) -> None:
    book = db.scalar(
        select(Book).where(
            Book.serial_number == serial_number
        )
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    db.delete(book)
    db.commit()
    logger.info("Book %s deleted", serial_number)


def update_book_status(
    db: Session,
    serial_number: str,
    status_data: BookStatusUpdate
) -> Book:

    book = db.scalar(
        select(Book).where(
            Book.serial_number == serial_number
        )
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    if status_data.is_borrowed:

        if not status_data.borrower_card_number:
            raise HTTPException(
                status_code=422,
                detail="Borrower card number is required"
            )

        if book.is_borrowed:
            raise HTTPException(
                status_code=409,
                detail="Book is already borrowed"
            )

        book.is_borrowed = True
        book.borrower_card_number = status_data.borrower_card_number
        book.borrowed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    else:
        book.is_borrowed = False
        book.borrower_card_number = None
        book.borrowed_at = None

    db.commit()
    db.refresh(book)
    action = "borrowed" if status_data.is_borrowed else "returned"
    logger.info("Book %s %s", serial_number, action)

    return book
