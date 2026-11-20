from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class BookCreate(BaseModel):
    serial_number: str = Field(pattern=r"^\d{6}$")
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)


class BookStatusUpdate(BaseModel):
    is_borrowed: bool
    borrower_card_number: str | None = Field(
        default=None,
        pattern=r"^\d{6}$",
        description="Required when is_borrowed is true.",
    )

    @model_validator(mode="after")
    def require_borrower_card_when_borrowed(self) -> "BookStatusUpdate":
        if self.is_borrowed and self.borrower_card_number is None:
            raise ValueError("borrower_card_number is required when borrowing")
        return self


class BookResponse(BaseModel):
    serial_number: str
    title: str
    author: str
    is_borrowed: bool
    borrower_card_number: str | None
    borrowed_at: datetime | None

    model_config = {
        "from_attributes": True
    }