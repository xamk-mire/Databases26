from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
    year: int
    isbn: str
    status: str  # AVAILABLE | OUT (no enforcement here on purpose)


@dataclass(frozen=True)
class Member:
    id: int
    name: str
    email: str
    joined_date: str  # ISO date string
    status: str  # ACTIVE | SUSPENDED


@dataclass(frozen=True)
class Loan:
    id: int
    book_id: int
    member_id: int
    loan_date: str  # ISO date string
    return_date: Optional[str]  # ISO date string or None
    status: str  # OUT | RETURNED
