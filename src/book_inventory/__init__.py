"""A simple book inventory management application using SQLite and Open Library API.

For simplicity, we only support adding books by ISBN number, fetching book information
from the Open Library API. To edit book information, you can directly edit the SQLite database
using a tool like DB Browser for SQLite (`sqlitebrowser`).

Use `uv run books -h` to see the available commands and options.
"""

import csv
import io
import json
import sqlite3
from typing import Any

import requests
import rich
import rich_click as click
from rich.prompt import Confirm, Prompt

from . import format as fmt
from .console import console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

SQL_BOOKS_CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS books (
    isbn13 INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    subtitle TEXT,
    authors TEXT,
    year INTEGER NOT NULL,
    is_hardcover BOOLEAN,
    notes TEXT
)"""

SQL_BOOKS_INSERT = """\
INSERT INTO books (isbn13, title, subtitle, authors, year, is_hardcover, notes)
VALUES (?, ?, ?, ?, ?, ?, ?)"""


def insert_book(
    isbn13: int,
    title: str,
    subtitle: str | None,
    authors: list[str],
    year: int,
    is_hardcover: bool,
    notes: str | None = None,
) -> None:
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            SQL_BOOKS_INSERT,
            (isbn13, title, subtitle, "; ".join(authors), year, is_hardcover, notes),
        )
        conn.commit()


def show_single_book(
    isbn13, title, subtitle, authors_str, year, is_hardcover, notes
) -> None:
    authors = authors_str.split("; ") if authors_str else []
    console.print(f"Book details for ISBN13 {isbn13}:")
    table = rich.table.Table(show_header=True)
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ISBN13", str(isbn13))
    table.add_row("Title", title)
    table.add_row("Subtitle", subtitle or "")
    table.add_row("Author(s)", "\n".join(authors))
    table.add_row("Publication Year", str(year))
    table.add_row("Hardcover", "Yes" if is_hardcover else "No")
    table.add_row("Notes", notes or "")
    console.print(table)


def isbn10_to_13(isbn10: int) -> int:
    """Convert an ISBN10 number to ISBN13."""
    # Check for maximum length of 10 digits for ISBN10
    if len(str(isbn10)) > 10:
        raise ValueError("ISBN10 must be at most a 10-digit number.")

    isbn_str = str(isbn10)
    # Pad with leading zeros if necessary to ensure it is 10 digits long
    isbn_str = isbn_str.zfill(10)

    # Create the ISBN13 by prefixing "978" and removing the ISBN10 check digit
    isbn13 = "978" + isbn_str[:-1]

    # Calculate the ISBN13 check digit
    # Alternate weights of 1 and 3, all 13 digits should sum to 0 (mod 10)
    total = 0
    for i, digit in enumerate(isbn13):
        if i % 2 == 0:
            total += int(digit)
        else:
            total += 3 * int(digit)
    check_digit = (10 - (total % 10)) % 10

    isbn13 += str(check_digit)
    return int(isbn13)


def validate_isbn13(isbn13: int) -> bool:
    """Validate that the given ISBN13 number is valid."""
    isbn_str = str(isbn13)
    if len(isbn_str) != 13 or not isbn_str.isdigit():
        return False

    total = 0
    for i, digit in enumerate(isbn_str):
        if i % 2 == 0:
            total += int(digit)
        else:
            total += 3 * int(digit)

    return total % 10 == 0


def init_db() -> None:
    # Create the books table if it doesn't exist
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute(SQL_BOOKS_CREATE_TABLE)
        conn.commit()


@click.group(context_settings=CONTEXT_SETTINGS)
def books() -> None:
    pass


@books.command(
    help="Add a book to the inventory by providing its ISBN number.",
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("isbn", type=int)
def add(isbn: int) -> None:
    # Convert ISBN10 to ISBN13 if necessary
    if len(str(isbn)) <= 10:
        isbn = isbn10_to_13(isbn)

    # Check that isbn is a 13-digit number
    if len(str(isbn)) != 13:
        console.print(fmt.error("ISBN must be a 13-digit number."))
        return

    if not validate_isbn13(isbn):
        console.print(fmt.error("Invalid ISBN13 number (check digit mismatch)."))
        return

    init_db()

    # Check if the book already exists in the database
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT isbn13, title, subtitle, authors, year, is_hardcover, notes "
            "FROM books WHERE isbn13 = ?",
            (isbn,),
        )
        if (found_book := cursor.fetchone()) is not None:
            console.print(
                fmt.error(f"A book with ISBN {isbn} already exists in the inventory.")
            )
            show_single_book(*found_book)
            return

    url = f"https://openlibrary.org/search.json?isbn={isbn}"
    console.print(f"Fetching book data for ISBN {isbn} from Open Library...")
    response = requests.get(url, timeout=60)
    book_info = {}
    book_found = False
    if response.status_code != 200:
        console.print(fmt.warning(f"Failed to fetch book data for ISBN {isbn}."))
    else:
        data = response.json()
        if data["numFound"] == 0:
            console.print(fmt.warning(f"No book found for ISBN {isbn}."))
        else:
            book_found = True
            doc = data["docs"][0]  # Take the first search result
            book_info = {
                "isbn13": isbn,
                "title": doc.get("title", ""),
                "subtitle": doc.get("subtitle", None),
                "authors": doc.get("author_name", []),  # List of strings
                "year": doc.get("first_publish_year", None),
            }
            if book_info["year"] is not None:
                book_info["year"] = int(book_info["year"])

    # Prompt the user for any missing information
    if not book_info.get("title"):
        while True:
            title = Prompt.ask("Please enter the book title", console=console).strip()
            if title:
                book_info["title"] = title
                break
            else:
                console.print(fmt.error("Title cannot be empty."))
    # Only prompt for subtitle if the book was not found in the API, since it's optional
    if book_info.get("subtitle") is None and not book_found:
        subtitle = Prompt.ask(
            "Please enter the book subtitle (optional)", console=console
        ).strip()
        book_info["subtitle"] = subtitle if subtitle else None
    if not book_info.get("authors"):
        while True:
            authors = Prompt.ask(
                "Please enter the book authors (;-separated)", console=console
            ).strip()
            book_info["authors"] = (
                [author.strip() for author in authors.split(";")] if authors else []
            )
            # Check that author list is non-empty and does not contain empty strings
            if book_info["authors"] and all(book_info["authors"]):
                break
            elif not book_info["authors"]:
                console.print(
                    fmt.error(
                        "Authors cannot be empty. Please enter at least one author."
                    )
                )
            else:
                console.print(
                    fmt.error(
                        "Author names cannot be empty. Please ensure all author names are valid."
                    )
                )
    if book_info.get("year") is None:
        while True:
            year_str = Prompt.ask(
                "Please enter the book publication year", console=console
            ).strip()
            if not year_str:
                console.print(fmt.error("Publication year cannot be empty."))
                continue
            try:
                year = int(year_str)
                book_info["year"] = year
                break
            except ValueError:
                console.print(fmt.error("Publication year must be an integer."))

    is_hardcover = Confirm.ask(
        "Is the book a hardcover edition?", console=console, default=False
    )
    book_info["is_hardcover"] = is_hardcover

    # Print the collected book information for confirmation
    console.print("\nCollected Book Information:")
    show_single_book(
        isbn13=isbn,
        title=book_info["title"],
        subtitle=book_info["subtitle"],
        authors_str="; ".join(book_info["authors"]),
        year=book_info["year"],
        is_hardcover=book_info["is_hardcover"],
        notes=book_info.get("notes"),
    )

    console.print()

    confirm_add = Confirm.ask(
        "Add this book to the inventory?", console=console, default=True
    )
    if not confirm_add:
        console.print("[red]Aborted.[/red]")
        return
    # Insert the book information into the database
    insert_book(
        isbn13=isbn,
        title=book_info["title"],
        subtitle=book_info["subtitle"],
        authors=book_info["authors"],
        year=book_info["year"],
        is_hardcover=book_info["is_hardcover"],
        notes=book_info.get("notes"),
    )

    console.print(fmt.success("Book added to the inventory."))


@books.command(
    help="List all books in the inventory.",
    context_settings=CONTEXT_SETTINGS,
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "csv"], case_sensitive=False),
    default="table",
    help="Output format",
)
@click.option(
    "--order",
    "-o",
    type=click.Choice(["isbn13", "title", "year"], case_sensitive=False),
    default="isbn13",
    help="Order by field",
)
@click.option("--desc", is_flag=True, help="Sort in descending order")
def list(format: str, order: str, desc: bool) -> None:
    init_db()

    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()

        if order == "title":
            order_by = "LOWER(title)"  # Case-insensitive sorting by title
        elif order == "year":
            order_by = "year IS NULL, year"  # Sort by year, with NULLs last
        else:  # Default to sorting by isbn13
            order_by = "isbn13"

        # Omit notes field in the listing for brevity, but it can be added if needed
        cursor.execute(
            f"SELECT isbn13, title, subtitle, authors, year, is_hardcover "
            f"FROM books ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
        )
        books = cursor.fetchall()
        if not books:
            console.print(fmt.warning("No books in the inventory."))
            return

        if format == "table":
            table = rich.table.Table(show_header=True, show_lines=True)
            table.add_column("ISBN13", style="cyan", no_wrap=True)
            table.add_column("Title", style="magenta")
            table.add_column("Subtitle", style="magenta")
            table.add_column("Author(s)", style="yellow")
            table.add_column("Year", style="green")
            table.add_column("Hardcover", style="red")

            for isbn13, title, subtitle, authors_str, year, is_hardcover in books:
                table.add_row(
                    str(isbn13),
                    title,
                    subtitle or "",
                    authors_str,
                    str(year) if year is not None else "",
                    "Yes" if is_hardcover else "No",
                )

            console.print(table)

        elif format == "json":
            books_list = []
            for isbn13, title, subtitle, authors_str, year, is_hardcover in books:
                books_list.append(
                    {
                        "isbn13": isbn13,
                        "title": title,
                        "subtitle": subtitle,
                        "authors": authors_str.split("; ") if authors_str else [],
                        "year": year,
                        "is_hardcover": is_hardcover,
                    }
                )
            console.print(json.dumps(books_list, indent=4))

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                ["ISBN13", "Title", "Subtitle", "Authors", "Year", "Hardcover"]
            )
            for isbn13, title, subtitle, authors_str, year, is_hardcover in books:
                writer.writerow(
                    [
                        isbn13,
                        title,
                        subtitle or "",
                        authors_str,
                        year if year is not None else "",
                        "Yes" if is_hardcover else "No",
                    ]
                )
            console.print(output.getvalue())


@books.command(
    help="Search for a book.",
    context_settings=CONTEXT_SETTINGS,
)
@click.option(
    "--title", "-t", type=str, multiple=True, help="Search by title (partial match)"
)
@click.option(
    "--author", "-a", type=str, multiple=True, help="Search by author (partial match)"
)
@click.option("--year", "-y", type=int, help="Search by publication year")
def search(title: tuple[str, ...], author: tuple[str, ...], year: int | None) -> None:
    init_db()

    # Build the query using parameter placeholders to avoid SQL injection.
    base_query = "SELECT isbn13, title, subtitle, authors, year, is_hardcover FROM books WHERE 1=1"
    params: list[Any] = []

    # Add title filters
    for title_part in title:
        # Use concatenation of title and subtitle for matching
        base_query += " AND (title || ' ' || IFNULL(subtitle, '')) LIKE ?"
        params.append(f"%{title_part}%")

    # Add author filters
    for author_part in author:
        base_query += " AND authors LIKE ?"
        params.append(f"%{author_part}%")

    # Add year filter if provided
    if year is not None:
        base_query += " AND year = ?"
        params.append(year)

    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute(base_query, params)
        results = cursor.fetchall()

    if not results:
        console.print(fmt.warning(f"No books found matching query."))
        return

    table = rich.table.Table(show_header=True, show_lines=True)
    table.add_column("ISBN13", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Subtitle", style="magenta")
    table.add_column("Author(s)", style="yellow")
    table.add_column("Year", style="green")
    table.add_column("Hardcover", style="red")

    for isbn13, title, subtitle, authors_str, year, is_hardcover in results:
        table.add_row(
            str(isbn13),
            title,
            subtitle or "",
            authors_str,
            str(year) if year is not None else "",
            "Yes" if is_hardcover else "No",
        )

    console.print(table)


@books.command(
    help="Show detailed information for a single book by ISBN.",
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("isbn", type=int)
def show(isbn: int) -> None:
    init_db()

    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT isbn13, title, subtitle, authors, year, is_hardcover, notes "
            "FROM books WHERE isbn13 = ?",
            (isbn,),
        )
        book = cursor.fetchone()

    if book is None:
        console.print(fmt.warning(f"No book found with ISBN {isbn}."))
        return

    show_single_book(*book)


@books.command(
    help="Export the book inventory as an SQL dump file.",
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("output_file", type=click.Path(writable=True))
def export(output_file: str) -> None:
    init_db()

    with sqlite3.connect("books.db") as conn:
        with open(output_file, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
    console.print(fmt.success(f"Book inventory exported to {output_file}."))


@books.command(
    "import",
    help="Import book inventory from an SQL dump file.",
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("input_file", type=click.Path(exists=True, readable=True))
def import_sql(input_file: str) -> None:
    # If books.db already exists, ask for confirmation before overwriting
    if (conn := sqlite3.connect("books.db")) is not None:
        conn.close()
        if not Confirm.ask(
            "[red]This will overwrite the existing book inventory. Do you want to continue?[/red]",
            console=console,
            default=False,
        ):
            console.print("[red]Aborted.[/red]")
            return

    with sqlite3.connect("books.db") as conn:
        with open(input_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
        # Drop the existing books table if it exists to avoid conflicts, then execute the SQL script
        conn.execute("DROP TABLE IF EXISTS books")
        conn.executescript(sql_script)
        conn.commit()
    console.print(fmt.success(f"Book inventory imported from {input_file}."))


if __name__ == "__main__":
    books()
