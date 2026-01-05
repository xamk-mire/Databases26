from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

BOOK_AVAILABLE = "AVAILABLE"
BOOK_OUT = "OUT"

MEMBER_ACTIVE = "ACTIVE"
MEMBER_SUSPENDED = "SUSPENDED"

LOAN_OUT = "OUT"
LOAN_RETURNED = "RETURNED"


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
    year: int
    isbn: str
    status: str  # AVAILABLE | OUT


@dataclass(frozen=True)
class Member:
    id: int
    name: str
    email: str
    joined_date: str  # YYYY-MM-DD
    status: str  # ACTIVE | SUSPENDED


@dataclass(frozen=True)
class Loan:
    id: int
    book_id: int
    member_id: int
    loan_date: str  # YYYY-MM-DD
    return_date: str  # empty string means NULL
    status: str  # OUT | RETURNED
