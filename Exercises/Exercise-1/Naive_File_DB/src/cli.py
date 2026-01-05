from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List

from . import commands


def _print_rows(rows: List[Dict[str, str]]) -> None:
    if not rows:
        print("(no results)")
        return
    # Simple pretty-print without dependencies
    keys = list(rows[0].keys())
    widths = {k: max(len(k), max(len(str(r.get(k, ""))) for r in rows)) for k in keys}
    header = " | ".join(k.ljust(widths[k]) for k in keys)
    sep = "-+-".join("-" * widths[k] for k in keys)
    print(header)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(k, "")).ljust(widths[k]) for k in keys))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="filedb", description="Naive file-based DB CLI (CSV)")
    p.add_argument("--data-dir", default="./data", help="Directory containing CSV files")
    sub = p.add_subparsers(dest="cmd", required=True)

    # add-book
    s = sub.add_parser("add-book", help="Add a new book")
    s.add_argument("--title", required=True)
    s.add_argument("--author", required=True)
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--isbn", required=True)

    # find-book
    s = sub.add_parser("find-book", help="Find books by title substring")
    s.add_argument("--title", required=True)

    # add-member
    s = sub.add_parser("add-member", help="Add a new member")
    s.add_argument("--name", required=True)
    s.add_argument("--email", required=True)

    # rename-member
    s = sub.add_parser("rename-member", help="Rename a member")
    s.add_argument("--member-id", type=int, required=True)
    s.add_argument("--name", required=True)

    # checkout
    s = sub.add_parser("checkout", help="Checkout a book to a member")
    s.add_argument("--book-id", type=int, required=True)
    s.add_argument("--member-id", type=int, required=True)

    # return
    s = sub.add_parser("return", help="Return a loan")
    s.add_argument("--loan-id", type=int, required=True)

    # member-loans
    s = sub.add_parser("member-loans", help="List loans for a member")
    s.add_argument("--member-id", type=int, required=True)
    s.add_argument("--include-returned", action="store_true")

    # overdue
    s = sub.add_parser("overdue", help="List overdue loans")
    s.add_argument("--days", type=int, default=14)

    # validate
    sub.add_parser("validate", help="Run integrity checks")

    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_dir = args.data_dir

    # Ensure data dir exists (but don't create files unless needed)
    os.makedirs(data_dir, exist_ok=True)

    try:
        if args.cmd == "add-book":
            book_id = commands.add_book(data_dir, args.title, args.author, args.year, args.isbn)
            print(f"Added book id={book_id}")

        elif args.cmd == "find-book":
            rows = commands.find_books_by_title(data_dir, args.title)
            _print_rows(rows)

        elif args.cmd == "add-member":
            member_id = commands.add_member(data_dir, args.name, args.email)
            print(f"Added member id={member_id}")

        elif args.cmd == "rename-member":
            ok = commands.rename_member(data_dir, args.member_id, args.name)
            print("OK" if ok else "Not found")

        elif args.cmd == "checkout":
            loan_id = commands.checkout(data_dir, args.book_id, args.member_id)
            print(f"Checked out. loan_id={loan_id}")

        elif args.cmd == "return":
            ok = commands.return_loan(data_dir, args.loan_id)
            print("OK" if ok else "Not found")

        elif args.cmd == "member-loans":
            rows = commands.member_loans(data_dir, args.member_id, include_returned=args.include_returned)
            _print_rows(rows)

        elif args.cmd == "overdue":
            rows = commands.overdue(data_dir, args.days)
            _print_rows(rows)

        elif args.cmd == "validate":
            problems = commands.validate_integrity(data_dir)
            if not problems:
                print("No problems found.")
            else:
                print("Problems:")
                for p in problems:
                    print(f"- {p}")
                return 2

        else:
            raise RuntimeError("Unknown command")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
