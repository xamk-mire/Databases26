from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from . import storage
from .models import (
    BOOK_AVAILABLE, BOOK_OUT,
    MEMBER_ACTIVE, MEMBER_SUSPENDED,
    LOAN_OUT, LOAN_RETURNED,
)

BOOK_HEADERS = ["id", "title", "author", "year", "isbn", "status"]
MEMBER_HEADERS = ["id", "name", "email", "joined_date", "status"]
LOAN_HEADERS = ["id", "book_id", "member_id", "loan_date", "return_date", "status"]


def paths(data_dir: str) -> Dict[str, str]:
    return {
        "books": os.path.join(data_dir, "books.csv"),
        "members": os.path.join(data_dir, "members.csv"),
        "loans": os.path.join(data_dir, "loans.csv"),
    }


def bootstrap(data_dir: str) -> None:
    p = paths(data_dir)
    storage.ensure_file(p["books"], BOOK_HEADERS)
    storage.ensure_file(p["members"], MEMBER_HEADERS)
    storage.ensure_file(p["loans"], LOAN_HEADERS)


# -----------------------
# Books
# -----------------------

def add_book(data_dir: str, title: str, author: str, year: int, isbn: str) -> int:
    p = paths(data_dir)
    bootstrap(data_dir)
    new_id = storage.next_id(p["books"])
    storage.append_row(p["books"], BOOK_HEADERS, {
        "id": str(new_id),
        "title": title,
        "author": author,
        "year": str(year),
        "isbn": isbn,
        "status": BOOK_AVAILABLE,
    })
    return new_id


def find_books_by_title(data_dir: str, query: str) -> List[Dict[str, str]]:
    p = paths(data_dir)
    bootstrap(data_dir)
    q = query.lower()
    out: List[Dict[str, str]] = []
    for row in storage.read_all(p["books"]):
        if q in (row.get("title", "").lower()):
            out.append(row)
    return out


# -----------------------
# Members
# -----------------------

def add_member(data_dir: str, name: str, email: str) -> int:
    p = paths(data_dir)
    bootstrap(data_dir)
    new_id = storage.next_id(p["members"])
    storage.append_row(p["members"], MEMBER_HEADERS, {
        "id": str(new_id),
        "name": name,
        "email": email,
        "joined_date": date.today().isoformat(),
        "status": MEMBER_ACTIVE,
    })
    return new_id


def rename_member(data_dir: str, member_id: int, new_name: str) -> bool:
    p = paths(data_dir)
    bootstrap(data_dir)
    return storage.update_by_id(p["members"], MEMBER_HEADERS, member_id, {"name": new_name})


# -----------------------
# Loans
# -----------------------

def checkout(data_dir: str, book_id: int, member_id: int) -> int:
    """Create a loan OUT entry. Intentionally uses slow scans and weak integrity checks."""
    p = paths(data_dir)
    bootstrap(data_dir)

    book = storage.find_by_id(p["books"], book_id)
    if not book:
        raise ValueError(f"Book {book_id} not found")

    member = storage.find_by_id(p["members"], member_id)
    if not member:
        raise ValueError(f"Member {member_id} not found")

    # TODO (students): enforce member status not SUSPENDED
    # TODO (students): enforce book not already OUT by checking existing loans or book.status

    # Naive rule: check book.status field only (can get out of sync with loans.csv)
    if book.get("status") == BOOK_OUT:
        raise ValueError(f"Book {book_id} is already OUT (according to books.csv)")

    loan_id = storage.next_id(p["loans"])
    storage.append_row(p["loans"], LOAN_HEADERS, {
        "id": str(loan_id),
        "book_id": str(book_id),
        "member_id": str(member_id),
        "loan_date": date.today().isoformat(),
        "return_date": "",
        "status": LOAN_OUT,
    })

    # Update book status (rewrite file)
    storage.update_by_id(p["books"], BOOK_HEADERS, book_id, {"status": BOOK_OUT})
    return loan_id


def return_loan(data_dir: str, loan_id: int) -> bool:
    p = paths(data_dir)
    bootstrap(data_dir)

    loan = storage.find_by_id(p["loans"], loan_id)
    if not loan:
        return False

    if loan.get("status") == LOAN_RETURNED:
        return True

    # Update loan record (rewrite file)
    updated = storage.update_by_id(p["loans"], LOAN_HEADERS, loan_id, {
        "status": LOAN_RETURNED,
        "return_date": date.today().isoformat(),
    })

    # Naively set book to AVAILABLE (even if multiple OUT loans exist -> intentional pain)
    try:
        book_id = int(loan.get("book_id") or "0")
        storage.update_by_id(p["books"], BOOK_HEADERS, book_id, {"status": BOOK_AVAILABLE})
    except ValueError:
        pass

    return updated


def member_loans(data_dir: str, member_id: int, include_returned: bool = False) -> List[Dict[str, str]]:
    p = paths(data_dir)
    bootstrap(data_dir)

    out: List[Dict[str, str]] = []
    for row in storage.read_all(p["loans"]):
        if row.get("member_id") != str(member_id):
            continue
        if not include_returned and row.get("status") == LOAN_RETURNED:
            continue
        out.append(row)
    return out


def overdue(data_dir: str, days: int) -> List[Dict[str, str]]:
    p = paths(data_dir)
    bootstrap(data_dir)

    cutoff = date.today() - timedelta(days=days)
    out: List[Dict[str, str]] = []
    for row in storage.read_all(p["loans"]):
        if row.get("status") != LOAN_OUT:
            continue
        loan_date_str = row.get("loan_date", "")
        try:
            ld = datetime.strptime(loan_date_str, "%Y-%m-%d").date()
        except ValueError:
            # Corrupt date -> treat as overdue (pain!)
            out.append(row)
            continue
        if ld <= cutoff:
            out.append(row)
    return out


def validate_integrity(data_dir: str) -> List[str]:
    """Run basic checks; returns a list of human-readable problems."""
    p = paths(data_dir)
    bootstrap(data_dir)

    problems: List[str] = []
    books = {row.get("id"): row for row in storage.read_all(p["books"])}
    members = {row.get("id"): row for row in storage.read_all(p["members"])}

    # Check loan references exist
    for row in storage.read_all(p["loans"]):
        bid = row.get("book_id")
        mid = row.get("member_id")
        if bid not in books:
            problems.append(f"Loan {row.get('id')} references missing book_id={bid}")
        if mid not in members:
            problems.append(f"Loan {row.get('id')} references missing member_id={mid}")

    # Check multiple OUT loans per book (should not happen)
    out_by_book: Dict[str, int] = {}
    for row in storage.read_all(p["loans"]):
        if row.get("status") == LOAN_OUT:
            bid = row.get("book_id", "")
            out_by_book[bid] = out_by_book.get(bid, 0) + 1
    for bid, count in out_by_book.items():
        if count > 1:
            problems.append(f"Book {bid} has {count} OUT loans (double checkout)")

    return problems
