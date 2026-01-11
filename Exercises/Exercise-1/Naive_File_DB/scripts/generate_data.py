"""
generate_data.py — File-based DB exercise dataset generator

Creates:
  - books.csv   (id,title,author,year,isbn,status)
  - members.csv (id,name,email,joined_date,status)
  - loans.csv   (id,book_id,member_id,loan_date,return_date,status)

Examples:
  # Small clean dataset
  python generate_data.py --books 50 --members 20 --loans 30 --out ./data

  # Large dataset for performance pain
  python generate_data.py --books 200000 --members 50000 --loans 150000 --out ./big --seed 1

  # Inject "bad data" for pain labs
  python generate_data.py --books 5000 --members 2000 --loans 4000 --out ./pain \
    --bad-refs 50 --double-checkout 50 --inconsistent 50 --schema-drift
"""

from __future__ import annotations
import argparse
import csv
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple


WORDS = [
    "Shadow",
    "Empire",
    "Storm",
    "Crystal",
    "Moon",
    "Iron",
    "Dawn",
    "Night",
    "River",
    "Star",
    "Garden",
    "Machine",
    "Signal",
    "Cipher",
    "Archive",
    "Labyrinth",
    "Echo",
    "Voyage",
    "Dust",
    "Code",
    "Fire",
    "Glass",
    "Whisper",
    "Quantum",
    "Atlas",
    "Circuit",
    "Harbor",
    "Phoenix",
    "Dream",
    "Halo",
]

FIRST_NAMES = [
    "Ada",
    "Alan",
    "Grace",
    "Donald",
    "Barbara",
    "Edsger",
    "Linus",
    "Tim",
    "Margaret",
    "Katherine",
    "Dennis",
    "Ken",
    "Guido",
    "James",
    "Frances",
    "John",
    "Claude",
    "Mary",
    "Satoshi",
    "Hedy",
]
LAST_NAMES = [
    "Lovelace",
    "Turing",
    "Hopper",
    "Knuth",
    "Liskov",
    "Dijkstra",
    "Torvalds",
    "Berners-Lee",
    "Hamilton",
    "Johnson",
    "Ritchie",
    "Thompson",
    "van Rossum",
    "Gosling",
    "Allen",
    "Backus",
    "Shannon",
    "Jackson",
    "Nakamoto",
    "Lamarr",
]


@dataclass
class Args:
    books: int
    members: int
    loans: int
    out: str
    seed: int
    start_date: date
    end_date: date
    out_ratio: float
    suspended_ratio: float
    bad_refs: int
    double_checkout: int
    inconsistent: int
    schema_drift: bool


def parse_date(s: str) -> date:
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def rand_date(rng: random.Random, start: date, end: date) -> date:
    if end < start:
        start, end = end, start
    delta_days = (end - start).days
    return start + timedelta(days=rng.randint(0, delta_days))


def make_title(rng: random.Random) -> str:
    # 2–4 words title
    n = rng.randint(2, 4)
    return " ".join(rng.choice(WORDS) for _ in range(n))


def make_author(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def isbn13(rng: random.Random) -> str:
    # Not a real checksum implementation (on purpose) — “file DB” doesn’t validate.
    # Creates a plausible 13-digit string.
    return "978" + "".join(str(rng.randint(0, 9)) for _ in range(10))


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_books(path: str, rng: random.Random, n: int, out_ratio: float) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "author", "year", "isbn", "status"])
        for i in range(1, n + 1):
            title = make_title(rng)
            author = make_author(rng)
            year = rng.randint(1950, 2024)
            status = "OUT" if rng.random() < out_ratio else "AVAILABLE"
            w.writerow([i, title, author, year, isbn13(rng), status])


def write_members(
    path: str,
    rng: random.Random,
    n: int,
    start: date,
    end: date,
    suspended_ratio: float,
) -> None:
    used_emails = set()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "email", "joined_date", "status"])
        for i in range(1, n + 1):
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            # Ensure unique-ish emails (still not enforced by anything in CSV…)
            base = name.lower().replace(" ", ".")
            email = f"{base}{rng.randint(1, 9999)}@example.com"
            while email in used_emails:
                email = f"{base}{rng.randint(1, 9999)}@example.com"
            used_emails.add(email)

            joined = rand_date(
                rng, start - timedelta(days=365 * 3), start
            )  # joined in the past
            status = "SUSPENDED" if rng.random() < suspended_ratio else "ACTIVE"
            w.writerow([i, name, email, joined.isoformat(), status])


def write_loans(
    path: str,
    rng: random.Random,
    n_loans: int,
    n_books: int,
    n_members: int,
    start: date,
    end: date,
    out_ratio: float,
    bad_refs: int,
    double_checkout: int,
    inconsistent: int,
) -> None:
    """
    Creates mostly valid loans:
      - OUT loans have empty return_date
      - RETURNED loans have a return_date >= loan_date

    Optional injections:
      - bad_refs: loans that reference non-existent book_id/member_id
      - double_checkout: extra OUT loans that reuse a currently-OUT book_id
      - inconsistent: contradictions (e.g., status OUT but has return_date)
    """

    # Track which books are currently checked out, to avoid double checkout in clean data.
    checked_out_books = set()

    # First generate base loans (mostly valid)
    rows: List[List[str]] = []
    next_id = 1

    # Helper to choose a book that is not currently OUT
    def choose_available_book_id() -> int:
        # Try a few times; if it's very dense, allow reuse (pain!)
        for _ in range(20):
            b = rng.randint(1, n_books)
            if b not in checked_out_books:
                return b
        return rng.randint(1, n_books)

    for _ in range(n_loans):
        book_id = choose_available_book_id()
        member_id = rng.randint(1, n_members)
        loan_dt = rand_date(rng, start, end)

        is_out = rng.random() < out_ratio
        if is_out:
            status = "OUT"
            return_dt = ""
            checked_out_books.add(book_id)
        else:
            status = "RETURNED"
            # Return 1–30 days later (cap at end date)
            return_dt_date = loan_dt + timedelta(days=rng.randint(1, 30))
            if return_dt_date > end:
                return_dt_date = end
            return_dt = return_dt_date.isoformat()

        rows.append(
            [
                str(next_id),
                str(book_id),
                str(member_id),
                loan_dt.isoformat(),
                return_dt,
                status,
            ]
        )
        next_id += 1

    # Inject bad references
    for _ in range(bad_refs):
        # 50/50 broken book_id vs broken member_id
        bad_book = rng.random() < 0.5
        book_id = (
            n_books + rng.randint(1, 5000) if bad_book else rng.randint(1, n_books)
        )
        member_id = (
            rng.randint(1, n_members)
            if bad_book
            else (n_members + rng.randint(1, 5000))
        )
        loan_dt = rand_date(rng, start, end)
        rows.append(
            [str(next_id), str(book_id), str(member_id), loan_dt.isoformat(), "", "OUT"]
        )
        next_id += 1

    # Inject double checkout (reusing books currently OUT)
    # Choose from checked_out_books if possible; otherwise just reuse random book ids.
    checked_out_list = list(checked_out_books) if checked_out_books else []
    for _ in range(double_checkout):
        if checked_out_list:
            book_id = rng.choice(checked_out_list)
        else:
            book_id = rng.randint(1, n_books)
        member_id = rng.randint(1, n_members)
        loan_dt = rand_date(rng, start, end)
        rows.append(
            [str(next_id), str(book_id), str(member_id), loan_dt.isoformat(), "", "OUT"]
        )
        next_id += 1

    # Inject inconsistent rows (contradict status/dates)
    for _ in range(inconsistent):
        book_id = rng.randint(1, n_books)
        member_id = rng.randint(1, n_members)
        loan_dt = rand_date(rng, start, end)

        if rng.random() < 0.5:
            # OUT but has return_date
            return_dt = (loan_dt + timedelta(days=rng.randint(1, 10))).isoformat()
            status = "OUT"
        else:
            # RETURNED but missing return_date
            return_dt = ""
            status = "RETURNED"
        rows.append(
            [
                str(next_id),
                str(book_id),
                str(member_id),
                loan_dt.isoformat(),
                return_dt,
                status,
            ]
        )
        next_id += 1

    # Write
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "book_id", "member_id", "loan_date", "return_date", "status"])
        w.writerows(rows)


def write_schema_drift_variants(out_dir: str) -> None:
    """
    Creates intentionally 'drifted' copies to demonstrate schema migration pain.
    - members_drift.csv: missing the status column for some rows
    - loans_drift.csv: extra column "notes" in header and some rows
    """
    members_src = os.path.join(out_dir, "members.csv")
    loans_src = os.path.join(out_dir, "loans.csv")

    # members_drift.csv: drop status from every 10th row
    dst_members = os.path.join(out_dir, "members_drift.csv")
    with (
        open(members_src, newline="", encoding="utf-8") as f_in,
        open(dst_members, "w", newline="", encoding="utf-8") as f_out,
    ):
        r = csv.reader(f_in)
        w = csv.writer(f_out)
        header = next(r)
        w.writerow(header)  # header stays the same (sneaky!)
        for idx, row in enumerate(r, start=1):
            if idx % 10 == 0:
                # Remove last column
                w.writerow(row[:-1])
            else:
                w.writerow(row)

    # loans_drift.csv: add a new column in header, but only populate sometimes
    dst_loans = os.path.join(out_dir, "loans_drift.csv")
    with (
        open(loans_src, newline="", encoding="utf-8") as f_in,
        open(dst_loans, "w", newline="", encoding="utf-8") as f_out,
    ):
        r = csv.reader(f_in)
        w = csv.writer(f_out)
        header = next(r)
        w.writerow(header + ["notes"])
        for idx, row in enumerate(r, start=1):
            if idx % 7 == 0:
                w.writerow(row + ["manual override"])
            else:
                w.writerow(row)


def build_args() -> Args:
    p = argparse.ArgumentParser()
    p.add_argument("--books", type=int, default=5000)
    p.add_argument("--members", type=int, default=2000)
    p.add_argument("--loans", type=int, default=4000)
    p.add_argument("--out", type=str, default="../data")
    p.add_argument("--seed", type=int, default=42)

    p.add_argument("--start-date", type=str, default="2024-01-01")
    p.add_argument("--end-date", type=str, default="2024-12-31")

    p.add_argument(
        "--out-ratio",
        type=float,
        default=0.35,
        help="Fraction of loans/books that are OUT",
    )
    p.add_argument(
        "--suspended-ratio",
        type=float,
        default=0.10,
        help="Fraction of members that are SUSPENDED",
    )

    # pain injection knobs
    p.add_argument(
        "--bad-refs",
        type=int,
        default=0,
        help="Add N loans referencing missing book_id/member_id",
    )
    p.add_argument(
        "--double-checkout",
        type=int,
        default=0,
        help="Add N extra OUT loans reusing an OUT book_id",
    )
    p.add_argument(
        "--inconsistent",
        type=int,
        default=0,
        help="Add N inconsistent loans (status/date mismatch)",
    )
    p.add_argument(
        "--schema-drift", action="store_true", help="Also output drifted CSV variants"
    )

    ns = p.parse_args()
    return Args(
        books=ns.books,
        members=ns.members,
        loans=ns.loans,
        out=ns.out,
        seed=ns.seed,
        start_date=parse_date(ns.start_date),
        end_date=parse_date(ns.end_date),
        out_ratio=ns.out_ratio,
        suspended_ratio=ns.suspended_ratio,
        bad_refs=ns.bad_refs,
        double_checkout=ns.double_checkout,
        inconsistent=ns.inconsistent,
        schema_drift=ns.schema_drift,
    )


def main() -> None:
    a = build_args()
    rng = random.Random(a.seed)
    ensure_dir(a.out)

    books_path = os.path.join(a.out, "books.csv")
    members_path = os.path.join(a.out, "members.csv")
    loans_path = os.path.join(a.out, "loans.csv")

    write_books(books_path, rng, a.books, a.out_ratio)
    write_members(
        members_path, rng, a.members, a.start_date, a.end_date, a.suspended_ratio
    )
    write_loans(
        loans_path,
        rng,
        a.loans,
        a.books,
        a.members,
        a.start_date,
        a.end_date,
        a.out_ratio,
        a.bad_refs,
        a.double_checkout,
        a.inconsistent,
    )

    if a.schema_drift:
        write_schema_drift_variants(a.out)

    print("Generated:")
    print(f"  {books_path}")
    print(f"  {members_path}")
    print(f"  {loans_path}")
    if a.schema_drift:
        print(f"  {os.path.join(a.out, 'members_drift.csv')}")
        print(f"  {os.path.join(a.out, 'loans_drift.csv')}")


if __name__ == "__main__":
    main()
