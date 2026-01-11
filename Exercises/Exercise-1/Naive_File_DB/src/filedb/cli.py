from __future__ import annotations

import argparse
import os
from datetime import date, timedelta
from typing import Dict, List, Optional

from dateutil.parser import isoparse

from .storage import read_csv_dicts, write_csv_dicts, next_id_naive, find_by_id, update_row_by_id


DEFAULT_DATA_DIR = os.environ.get("FILEDB_DATA", os.path.join(os.getcwd(), "data"))
BOOKS_CSV = "books.csv"
MEMBERS_CSV = "members.csv"
LOANS_CSV = "loans.csv"


def path_for(data_dir: str, filename: str) -> str:
    return os.path.join(data_dir, filename)


def cmd_init_data(args: argparse.Namespace) -> int:
    os.makedirs(args.data_dir, exist_ok=True)

    books_path = path_for(args.data_dir, BOOKS_CSV)
    members_path = path_for(args.data_dir, MEMBERS_CSV)
    loans_path = path_for(args.data_dir, LOANS_CSV)

    if not os.path.exists(books_path):
        write_csv_dicts(
            books_path,
            fieldnames=["id", "title", "author", "year", "isbn", "status"],
            rows=[
                {"id": 1, "title": "Dune", "author": "Frank Herbert", "year": 1965, "isbn": "9780441172719", "status": "AVAILABLE"},
                {"id": 2, "title": "Neuromancer", "author": "William Gibson", "year": 1984, "isbn": "9780441569595", "status": "AVAILABLE"},
                {"id": 3, "title": "Foundation", "author": "Isaac Asimov", "year": 1951, "isbn": "9780553293357", "status": "OUT"},
            ],
        )

    if not os.path.exists(members_path):
        write_csv_dicts(
            members_path,
            fieldnames=["id", "name", "email", "joined_date", "status"],
            rows=[
                {"id": 1, "name": "Ada Lovelace", "email": "ada.lovelace@example.com", "joined_date": "2023-01-15", "status": "ACTIVE"},
                {"id": 2, "name": "Alan Turing", "email": "alan.turing@example.com", "joined_date": "2023-02-03", "status": "ACTIVE"},
                {"id": 3, "name": "Grace Hopper", "email": "grace.hopper@example.com", "joined_date": "2023-03-21", "status": "ACTIVE"},
            ],
        )

    if not os.path.exists(loans_path):
        write_csv_dicts(
            loans_path,
            fieldnames=["id", "book_id", "member_id", "loan_date", "return_date", "status"],
            rows=[
                {"id": 1, "book_id": 3, "member_id": 1, "loan_date": "2024-01-05", "return_date": "", "status": "OUT"},
                {"id": 2, "book_id": 2, "member_id": 2, "loan_date": "2024-01-10", "return_date": "2024-01-18", "status": "RETURNED"},
            ],
        )

    print(f"Initialized data in: {args.data_dir}")
    return 0


def cmd_add_book(args: argparse.Namespace) -> int:
    books_path = path_for(args.data_dir, BOOKS_CSV)
    rows = read_csv_dicts(books_path)
    new_id = next_id_naive(rows)

    # TODO(student): validate fields, enforce allowed statuses, generate/validate ISBN, etc.
    row = {
        "id": new_id,
        "title": args.title,
        "author": args.author,
        "year": args.year,
        "isbn": args.isbn or "",
        "status": "AVAILABLE",
    }
    rows.append({k: str(v) for k, v in row.items()})
    write_csv_dicts(books_path, fieldnames=["id", "title", "author", "year", "isbn", "status"], rows=rows)
    print(f"Added book id={new_id}")
    return 0


def cmd_find_book(args: argparse.Namespace) -> int:
    books_path = path_for(args.data_dir, BOOKS_CSV)
    rows = read_csv_dicts(books_path)

    q = (args.title or "").strip().lower()
    matches = []
    for r in rows:
        title = (r.get("title") or "").lower()
        if q in title:
            matches.append(r)

    # NOTE: Linear scan on purpose. No index.
    for r in matches[: args.limit]:
        print(f'{r.get("id")} | {r.get("title")} | {r.get("author")} | {r.get("year")} | {r.get("status")}')
    print(f"Matches: {len(matches)}")
    return 0


def cmd_add_member(args: argparse.Namespace) -> int:
    members_path = path_for(args.data_dir, MEMBERS_CSV)
    rows = read_csv_dicts(members_path)
    new_id = next_id_naive(rows)

    # TODO(student): enforce unique email, validate email format, etc.
    today = date.today().isoformat()
    row = {
        "id": new_id,
        "name": args.name,
        "email": args.email,
        "joined_date": today,
        "status": "ACTIVE",
    }
    rows.append({k: str(v) for k, v in row.items()})
    write_csv_dicts(members_path, fieldnames=["id", "name", "email", "joined_date", "status"], rows=rows)
    print(f"Added member id={new_id}")
    return 0


def cmd_checkout(args: argparse.Namespace) -> int:
    books_path = path_for(args.data_dir, BOOKS_CSV)
    members_path = path_for(args.data_dir, MEMBERS_CSV)
    loans_path = path_for(args.data_dir, LOANS_CSV)

    books = read_csv_dicts(books_path)
    members = read_csv_dicts(members_path)
    loans = read_csv_dicts(loans_path)

    book = find_by_id(books, args.book_id)
    member = find_by_id(members, args.member_id)

    # TODO(student): proper errors + exit codes
    if book is None:
        raise SystemExit(f"Book id={args.book_id} not found")
    if member is None:
        raise SystemExit(f"Member id={args.member_id} not found")

    # TODO(student): enforce business rules
    # - no checkout if book already OUT
    # - no checkout if member SUSPENDED
    # - avoid race conditions / lost updates
    if (book.get("status") or "").upper() == "OUT":
        raise SystemExit(f"Book id={args.book_id} is already OUT")

    loan_id = next_id_naive(loans)
    loan_date = date.today().isoformat()
    loans.append(
        {
            "id": str(loan_id),
            "book_id": str(args.book_id),
            "member_id": str(args.member_id),
            "loan_date": loan_date,
            "return_date": "",
            "status": "OUT",
        }
    )

    # Mark book as OUT
    update_row_by_id(books, args.book_id, {"status": "OUT"})

    # Writes are not atomic (on purpose): multiple files, multiple writes.
    write_csv_dicts(loans_path, fieldnames=["id", "book_id", "member_id", "loan_date", "return_date", "status"], rows=loans)
    write_csv_dicts(books_path, fieldnames=["id", "title", "author", "year", "isbn", "status"], rows=books)

    print(f"Checked out: loan_id={loan_id}")
    return 0


def cmd_return(args: argparse.Namespace) -> int:
    books_path = path_for(args.data_dir, BOOKS_CSV)
    loans_path = path_for(args.data_dir, LOANS_CSV)

    books = read_csv_dicts(books_path)
    loans = read_csv_dicts(loans_path)

    loan = find_by_id(loans, args.loan_id)
    if loan is None:
        raise SystemExit(f"Loan id={args.loan_id} not found")

    if (loan.get("status") or "").upper() == "RETURNED":
        print("Loan already returned")
        return 0

    # Update loan
    return_date = date.today().isoformat()
    update_row_by_id(loans, args.loan_id, {"status": "RETURNED", "return_date": return_date})

    # Update book status back to AVAILABLE
    try:
        book_id = int(loan.get("book_id") or "0")
    except ValueError:
        raise SystemExit("Corrupt loan record: book_id is not an int")

    update_row_by_id(books, book_id, {"status": "AVAILABLE"})

    # Again: multiple file rewrites, no transaction.
    write_csv_dicts(loans_path, fieldnames=["id", "book_id", "member_id", "loan_date", "return_date", "status"], rows=loans)
    write_csv_dicts(books_path, fieldnames=["id", "title", "author", "year", "isbn", "status"], rows=books)

    print(f"Returned loan id={args.loan_id}")
    return 0


def cmd_member_loans(args: argparse.Namespace) -> int:
    loans_path = path_for(args.data_dir, LOANS_CSV)
    loans = read_csv_dicts(loans_path)

    sid = str(args.member_id)
    rows = [r for r in loans if (r.get("member_id") == sid)]
    for r in rows[: args.limit]:
        print(f'loan={r.get("id")} book={r.get("book_id")} loan_date={r.get("loan_date")} return_date={r.get("return_date")} status={r.get("status")}')
    print(f"Loans for member {args.member_id}: {len(rows)}")
    return 0


def cmd_overdue(args: argparse.Namespace) -> int:
    loans_path = path_for(args.data_dir, LOANS_CSV)
    loans = read_csv_dicts(loans_path)

    cutoff = date.today() - timedelta(days=args.days)
    overdue = []
    for r in loans:
        if (r.get("status") or "").upper() != "OUT":
            continue
        try:
            loan_dt = isoparse(r.get("loan_date") or "").date()
        except Exception:
            # Corrupt dates should hurt.
            continue
        if loan_dt < cutoff:
            overdue.append(r)

    for r in overdue[: args.limit]:
        print(f'loan={r.get("id")} book={r.get("book_id")} member={r.get("member_id")} loan_date={r.get("loan_date")}')
    print(f"Overdue (>{args.days} days): {len(overdue)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="filedb", description="Naïve file-based database CLI (intentionally painful).")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Directory containing CSV files (default: ./data or $FILEDB_DATA)")

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init-data", help="Create example CSV files if missing")
    s.set_defaults(func=cmd_init_data)

    s = sub.add_parser("add-book", help="Add a book to books.csv")
    s.add_argument("--title", required=True)
    s.add_argument("--author", required=True)
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--isbn", default="")
    s.set_defaults(func=cmd_add_book)

    s = sub.add_parser("find-book", help="Search books by title (substring, case-insensitive)")
    s.add_argument("--title", required=True)
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_find_book)

    s = sub.add_parser("add-member", help="Add a member to members.csv")
    s.add_argument("--name", required=True)
    s.add_argument("--email", required=True)
    s.set_defaults(func=cmd_add_member)

    s = sub.add_parser("checkout", help="Create a loan and mark the book OUT")
    s.add_argument("--book-id", type=int, required=True)
    s.add_argument("--member-id", type=int, required=True)
    s.set_defaults(func=cmd_checkout)

    s = sub.add_parser("return", help="Return a loan and mark book AVAILABLE")
    s.add_argument("--loan-id", type=int, required=True)
    s.set_defaults(func=cmd_return)

    s = sub.add_parser("member-loans", help="List loans for a member")
    s.add_argument("--member-id", type=int, required=True)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_member_loans)

    s = sub.add_parser("overdue", help="List overdue OUT loans")
    s.add_argument("--days", type=int, default=14)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_overdue)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
