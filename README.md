# Library API

A small FastAPI service for library staff to manage the books held by a library. It stores each book's six-digit serial number, title, author, availability, and the card number and timestamp for its current loan. The database is PostgreSQL.

Authentication and authorization are intentionally out of scope for this task.

## Additional comments

The implementation is intentionally kept small for this assignment:

- The database has one `books` table. Borrower card numbers are stored on the current book loan instead of introducing a separate borrowers/users table and a foreign key. This means the API does not verify that a card belongs to a registered library member or maintain borrower records.
- Only the current loan is represented. Returning a book clears its borrower card number and borrow timestamp, so the API does not retain loan history.
- The service rejects a loan when it reads the book as already borrowed, but the read and update are not atomic. Simultaneous requests could both observe an available book and overwrite the borrower information. A higher-concurrency deployment should use an atomic conditional update or row locking, and test that behavior.

These are scope choices for the recruitment task, not recommendations for a production library system.

## Features

- Add a book and list all books.
- Delete a book by its serial number.
- Mark a book as borrowed or available.
- Record the borrower's six-digit library card number and the time of borrowing.
- Validate request bodies and path parameters with Pydantic and FastAPI.
- Apply database schema migrations with Alembic.
- Log successful book changes and failed requests without logging borrower card numbers or request payloads.

## Run with Docker Compose

Prerequisites: Docker Engine or Docker Desktop with the Compose plugin.

From the project root, run:

```shell
docker compose up --build
```

Compose starts PostgreSQL, waits for its health check, then builds and starts the API. The API container runs `alembic upgrade head` before starting Uvicorn. The database is persisted in the `postgres_data` volume.

- API: <http://localhost:8000>
- Interactive API documentation: <http://localhost:8000/docs>
- Alternative API documentation: <http://localhost:8000/redoc>

Stop the services with `Ctrl+C`. To stop and remove the containers while keeping database data, run `docker compose down`. To also delete the database volume and its data, run `docker compose down --volumes`.

### Configuration and secrets

The API requires one environment setting: `DATABASE_URL`. For this local project, Docker Compose provides it directly in `docker-compose.yml`. Compose also provides `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` to initialize the local PostgreSQL container. These values are development conveniences, not production credentials. In higher environments, supply the database connection string through the deployment platform's secret management rather than storing credentials in the Compose file or source code.

## Logs

The API writes logs to standard output. Successful book creation, deletion, borrowing, and return are logged with the book serial number. Failed HTTP responses are logged with the request method, path, and status code; unhandled request exceptions are logged with a traceback. Request bodies, headers, query strings, and borrower card numbers are not logged.

With Docker Compose, view the API logs with:

```shell
docker compose logs api
```

Follow new log entries with `docker compose logs -f api`. When running the API locally, logs appear in the Uvicorn terminal.

## API

All endpoints are under `/books`. Serial numbers must contain six digits. Titles and authors must contain between 1 and 255 characters.

### Create a book

`POST /books`

```json
{
  "serial_number": "123456",
  "title": "The Left Hand of Darkness",
  "author": "Ursula K. Le Guin"
}
```

Returns `201 Created` with the book. A newly created book is available, and its `borrower_card_number` and `borrowed_at` values are `null`. Returns `409 Conflict` if that serial number already exists, or `422 Unprocessable Entity` if the request is invalid.

### List all books

`GET /books`

Returns `200 OK` with a JSON array of books. The array is empty if no books have been added.

### Update a book's availability

`PATCH /books/{serial_number}/status`

To borrow a book, provide the borrower's six-digit card number:

```json
{
  "is_borrowed": true,
  "borrower_card_number": "654321"
}
```

To return it, set `is_borrowed` to `false`:

```json
{
  "is_borrowed": false
}
```

Returns `200 OK` with the updated book. Borrowing records the current card number and timestamp. Returning clears both fields. Returns `404 Not Found` if the book does not exist, `409 Conflict` if it is already borrowed, or `422 Unprocessable Entity` for an invalid path or request body.

### Delete a book

`DELETE /books/{serial_number}`

Returns `204 No Content` when the book is deleted. Returns `404 Not Found` if it does not exist, or `422 Unprocessable Entity` if the serial number is not six digits.

### Book response

Book responses have this shape:

```json
{
  "serial_number": "123456",
  "title": "The Left Hand of Darkness",
  "author": "Ursula K. Le Guin",
  "is_borrowed": true,
  "borrower_card_number": "654321",
  "borrowed_at": "2026-11-20T12:34:56.123456"
}
```

`borrowed_at` is a timezone-naive ISO 8601 datetime representing UTC while the book is borrowed; the API omits a timezone suffix. Both loan fields are `null` when it is available.

## Run tests

Install the project dependencies, then run:

```shell
python -m pytest -q
```

The tests use FastAPI's `TestClient` and an isolated in-memory SQLite database. They do not connect to or modify the PostgreSQL database used by the application.

## Project layout

```text
app/
  api/          HTTP routes
  db/           Database engine and session dependency
  models/       SQLAlchemy database models
  schemas/      Pydantic request and response schemas
  services/     Book operations and business rules
alembic/        Database migrations
tests/          Pytest API tests
Dockerfile      API container image
docker-compose.yml
```