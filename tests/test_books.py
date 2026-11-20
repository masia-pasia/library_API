import logging
from datetime import datetime

import pytest


def create_book(client, serial_number="123456"):
    return client.post(
        "/books",
        json={
            "serial_number": serial_number,
            "title": "The Left Hand of Darkness",
            "author": "Ursula K. Le Guin",
        },
    )


def test_create_and_list_books(client):
    response = create_book(client)

    assert response.status_code == 201
    assert response.json() == {
        "serial_number": "123456",
        "title": "The Left Hand of Darkness",
        "author": "Ursula K. Le Guin",
        "is_borrowed": False,
        "borrower_card_number": None,
        "borrowed_at": None,
    }

    books_response = client.get("/books")
    assert books_response.status_code == 200
    assert books_response.json() == [response.json()]


@pytest.mark.parametrize("serial_number", ["12345", "1234567", "ABC123"])
def test_create_rejects_invalid_serial_number(client, serial_number):
    response = create_book(client, serial_number)

    assert response.status_code == 422


def test_book_id_paths_require_six_digits(client):
    delete_response = client.delete("/books/12345")
    status_response = client.patch(
        "/books/12345/status",
        json={"is_borrowed": False},
    )

    assert delete_response.status_code == 422
    assert status_response.status_code == 422


def test_borrowing_requires_six_digit_card_number(client):
    missing_card_response = client.patch(
        "/books/123456/status",
        json={"is_borrowed": True},
    )
    invalid_card_response = client.patch(
        "/books/123456/status",
        json={"is_borrowed": True, "borrower_card_number": "12345"},
    )

    assert missing_card_response.status_code == 422
    assert invalid_card_response.status_code == 422


def test_borrow_and_return_book(client):
    assert create_book(client).status_code == 201

    borrow_response = client.patch(
        "/books/123456/status",
        json={"is_borrowed": True, "borrower_card_number": "654321"},
    )

    assert borrow_response.status_code == 200
    borrowed_book = borrow_response.json()
    assert borrowed_book["is_borrowed"] is True
    assert borrowed_book["borrower_card_number"] == "654321"
    assert borrowed_book["borrowed_at"] is not None
    assert datetime.fromisoformat(borrowed_book["borrowed_at"]).tzinfo is None

    return_response = client.patch(
        "/books/123456/status",
        json={"is_borrowed": False},
    )

    assert return_response.status_code == 200
    returned_book = return_response.json()
    assert returned_book["is_borrowed"] is False
    assert returned_book["borrower_card_number"] is None
    assert returned_book["borrowed_at"] is None


def test_duplicate_book_and_missing_book_responses(client):
    assert create_book(client).status_code == 201

    duplicate_response = create_book(client)
    missing_delete_response = client.delete("/books/999999")
    missing_status_response = client.patch(
        "/books/999999/status",
        json={"is_borrowed": False},
    )

    assert duplicate_response.status_code == 409
    assert missing_delete_response.status_code == 404
    assert missing_status_response.status_code == 404


def test_failed_requests_are_logged(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app.main"):
        missing_response = client.delete("/books/999999")
        invalid_path_response = client.delete("/books/123")

    assert missing_response.status_code == 404
    assert invalid_path_response.status_code == 422
    assert "DELETE /books/999999 returned 404" in caplog.text
    assert "DELETE /books/123 returned 422" in caplog.text