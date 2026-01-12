# Exercise: File-Based Data Management (Pre-Database Era)

You’ve been dropped into a world **before relational databases**.  
You still need to store, update, and query data — but the only tools you have are **text files** and your own code.

This exercise is about **data management**, not “building a DB.”  
You are implementing the kind of procedures organizations used with **flat files**: ledgers, clerks, reports, and overnight batch jobs.

You will manage three “tables” stored as CSV files:

- `books.csv` — books in the library
- `members.csv` — library members
- `loans.csv` — loans (checkouts / returns)

---

## Learning outcomes

By the end, you should have a better understanding of (using failures you observed):

- how data management worked with **flat files**, conventions, and batch processing
- why **search** is slow without indexes (full scans)
- why **updates** are hard without record/page structures (rewrite vs append + compaction)
- why **concurrency** (two clerks writing at once) causes duplicate IDs and lost updates
- why **crashes** corrupt files without journaling/transactions
- why **constraints** (unique keys, foreign keys, valid values) matter
- why **schema changes** (adding a column) are painful without migrations
- why you gradually reinvent DB features (locking, indexing, logs) if you keep patching

---

## The scenario (1985 library)

There is no database server. There is no SQL. There is no “safe update.”

You have:

- a shared folder (your `data/` directory)
- CSV files as “ledgers”
- a CLI used by clerks for day-to-day operations
- “overnight batch jobs” (scripts you run periodically) to verify/reconcile/rebuild data

Your mission is to make this system **usable enough** that a clerk could run it, while documenting the pain along the way.

---

## Project tour: what each file is and why it exists

### Code

- `src/filedb/__main__.py`  
  Makes `python -m src.filedb ...` work. It’s the module entrypoint that calls the CLI.

- `src/filedb/cli.py`  
  The command-line program. This is where “clerks’ actions” live:

  - parsing command arguments
  - loading CSV ledgers
  - applying record-keeping rules (validation, business rules)
  - writing updated ledgers back to disk

- `src/filedb/storage.py`  
  Low-level CSV I/O helpers (intentionally naïve):

  - reads whole files into memory
  - writes whole files back for updates
  - provides a naïve `next_id` (`max(id)+1`) that is _race-condition friendly_

  This file exists to separate “data handling mechanics” from “clerks’ procedures” in `cli.py`.

- `src/filedb/models.py`  
  Optional dataclasses (Book/Member/Loan). You can use them for cleaner code, but the system ultimately persists as CSV.
  This file exists to make the “shape of records” explicit in code.

### Scripts

- `scripts/generate_data.py`  
   A dataset generator used to create **small or large ledgers** on demand.  
   This is especially useful for the “feel the pain” labs where you need big files to observe slow scans and expensive rewrites.

### Data (your ledgers)

- `data/books.csv`  
  The book ledger: one row per book.

- `data/members.csv`  
  The member ledger: one row per member.

- `data/loans.csv`  
  The loan ledger: one row per checkout/return event.

**Important:** CSV does not enforce anything. Your code and procedures must enforce:

- allowed values
- uniqueness rules
- referential integrity (loan rows must reference real book/member rows)

---

## Setup

Requires Python **3.10+**.

#### 1. Ensure you are in correct working folder

```bash
cd Naive_File_DB
```

- **Changes your current directory** to the project folder named `Naive_File_DB`.
- After this, any relative paths (like `.venv` or `requirements.txt`) are looked up inside that folder.

#### 2. Create virtual environment

```bash
python -m venv .venv
```

- Creates a **Python virtual environment** in a folder named `.venv`.
- A virtual environment is an isolated “mini Python install” for this project, so packages you install don’t affect your system-wide Python (and vice versa).
- Result: you’ll see a new `.venv/` directory appear.

#### 3. Activate virtual environment

###### A) Windows users

```bash
.venv\Scripts\Activate.ps1
```

- Activates the virtual environment on **Windows PowerShell**.
- Same effect as `source ...` on macOS/Linux: it redirects `python`/`pip` to use the `.venv` environment.
- Note: Windows uses backslashes `\` in paths.

##### B) Mac users

```bash
source .venv/bin/activate
```

- **Activates** the virtual environment on macOS/Linux.
- This updates your shell so:

  - `python` points to `.venv`’s Python
  - `pip` installs packages into `.venv` instead of system Python

- Usually your terminal prompt changes (often shows `(.venv)`).

#### Install dependencies

```bash
pip install -r requirements.txt
```

- Uses `pip` to **install all required dependencies** listed in `requirements.txt`.
- Because you activated `.venv` first, these packages install into the virtual environment (not globally).

---

## Using the dataset generator (scripts/generate_data.py)

You can use the generator any time you need **larger files** to make the problems obvious.

### Generate small clean data into `./data` (overwrites existing files)

```bash
python scripts/generate_data.py --books 50 --members 20 --loans 30 --out ./data
```

### Generate “big” data for performance pain

```bash
python scripts/generate_data.py --books 50000 --members 20000 --loans 40000 --out ./data --seed 1
```

### Generate “bad data” (for broken references, inconsistent statuses, schema drift)

```bash
python scripts/generate_data.py --books 5000 --members 2000 --loans 4000 --out ./data \
  --bad-refs 50 --double-checkout 50 --inconsistent 50 --schema-drift
```

**What it changes in practice:**  
It writes new versions of `books.csv`, `members.csv`, and `loans.csv` into the folder you specify with `--out`.

> Tip: If you want to keep multiple datasets, generate to a new folder:  
> `--out ./datasets/big1` and then run the CLI with `--data-dir ./datasets/big1`

---

## Quickstart (get it running once)

### 1) See what commands exist

```bash
python -m src.filedb --help
```

**In practice:** a clerk asks “what can I do with this system?” This is your “menu of procedures.”

### 2) Create sample ledgers (if missing)

```bash
python -m src.filedb init-data
```

**In practice:** you’re setting up the filing cabinets. If files already exist, it won’t overwrite them.

> If you want more data than the small starter files, use the generator instead:  
> `python scripts/generate_data.py --books 50 --members 20 --loans 30 --out ./data`

### 3) Search for a book by title

```bash
python -m src.filedb find-book --title dune
```

**In practice:** a clerk flips through the entire book ledger looking for a matching title.
This is a full-file scan (slow when the ledger is large).

---

## A day in the life: step-by-step walkthrough

This is a realistic “clerk workflow” using the system.

### Step 1 — Add a new member

```bash
python -m src.filedb add-member --name "Ada Lovelace" --email "ada@example.com"
```

**What it does in practice:**

- reads `members.csv`
- picks a new member ID (currently naïve: `max(id)+1`)
- appends a row
- rewrites the full `members.csv` file

### Step 2 — Add a new book

```bash
python -m src.filedb add-book --title "Dune" --author "Frank Herbert" --year 1965 --isbn "9780441172719"
```

**What it does in practice:**

- reads `books.csv`
- allocates a new ID
- writes a row with status `AVAILABLE`
- rewrites `books.csv`

### Step 3 — Check out a book

```bash
python -m src.filedb checkout --book-id 1 --member-id 1
```

**What it does in practice:**

- reads `books.csv`, `members.csv`, `loans.csv`
- creates a new row in `loans.csv` with status `OUT`
- updates the book’s row in `books.csv` to status `OUT`
- rewrites `loans.csv` and `books.csv`

### Step 4 — Return a book

```bash
python -m src.filedb return --loan-id 1
```

**What it does in practice:**

- updates the loan row to `RETURNED` + sets `return_date`
- updates the book status back to `AVAILABLE`
- rewrites `loans.csv` and `books.csv`

### Step 5 — List a member’s loan history

```bash
python -m src.filedb member-loans --member-id 1
```

**What it does in practice:** scans the entire `loans.csv` and prints rows for that member.

### Step 6 — Find overdue loans

```bash
python -m src.filedb overdue --days 14
```

**What it does in practice:** scans the entire `loans.csv` and prints old `OUT` loans.

---

## What you must do (NO CODING REQUIRED)

The required part of this exercise is to **use** the file-based system like a pre-DB organization would, and document what happens.

### Task 1 — Inspect the “ledgers” (CSV files)

1. Run `init-data`
2. Open `data/books.csv`, `data/members.csv`, `data/loans.csv` in a text editor
3. Answer in your report:
   - What do empty fields mean (e.g., `return_date`)?
   - Which rules are implied but not enforced by CSV?
   - Which file(s) would need to be edited for a checkout? for a return?

### Task 2 — Execute a full workflow and explain it

Run this sequence and explain what happens to the files after each step:

```bash
python -m src.filedb init-data
python -m src.filedb add-member --name "Ada Lovelace" --email "ada@example.com"
python -m src.filedb add-book --title "Dune" --author "Frank Herbert" --year 1965 --isbn "9780441172719"
python -m src.filedb checkout --book-id 1 --member-id 1
python -m src.filedb return --loan-id 1
python -m src.filedb member-loans --member-id 1
```

In your report, for each command:

- which CSV files were read?
- which CSV files were rewritten?
- what could go wrong if the program crashes at the wrong time?

### Task 3 — “Feel the pain” mini-labs (measure + explain)

You will run three short demos and write down what you observe.

These labs work best with **big ledgers**. Use the generator to create them first:

```bash
python scripts/generate_data.py --books 50000 --members 20000 --loans 40000 --out ./data --seed 1
```

> Alternative: generate to a separate folder and use `--data-dir`:
>
> - `python scripts/generate_data.py ... --out ./datasets/big1`
> - `python -m src.filedb --data-dir ./datasets/big1 find-book --title the`

#### Lab A: Linear search

Run `find-book` several times and note that it scans the whole file:

```bash
python -m src.filedb find-book --title the
python -m src.filedb find-book --title dune
```

Explain why this becomes slow with large files.

#### Lab B: One update rewrites a whole file

Return a loan and observe that it rewrites entire files (`loans.csv` and `books.csv`).  
Explain why “updating one row” is expensive in flat-file storage.

> Tip: If your dataset doesn’t have an obvious OUT loan to return, generate data with a higher out-ratio:  
> `python scripts/generate_data.py --books 50000 --members 20000 --loans 40000 --out ./data --out-ratio 0.7`

#### Lab C: No transactions (partial failure)

Checkout touches **two files** (`loans.csv` + `books.csv`).  
Explain what inconsistent state would look like if the program crashed after updating one file but not the other.

> Tip: You can demonstrate this without coding by describing _which file_ would be updated first and what mismatch it creates.

> Optional “bad data” demo (still no coding):  
> Generate broken/inconsistent ledgers and inspect them:
>
> ```bash
> python scripts/generate_data.py --books 5000 --members 2000 --loans 4000 --out ./data \
>   --bad-refs 50 --double-checkout 50 --inconsistent 50 --schema-drift
> ```
>
> Then open the CSVs and describe what kinds of problems appear.

### Task 4 — Write the “binder rules” (procedures)

In a short section of your report (bullets are fine), write your organization’s “record keeping binder”:

- allowed statuses for books/members/loans
- what a valid loan looks like
- what you do if you find broken references (loan points to missing book/member)
- what you do if books and loans disagree about whether a book is OUT
- how you would handle schema changes (adding a column) in CSV

This is what pre-DB teams actually did: _document rules + run batch reconciliation_.

---

## Optional / extra tasks (CODING ENCOURAGED)

Everything below is optional. If you want hands-on coding, pick one or more.  
Each task includes **example code** and exactly **where to put it**.

### Extra Task 1 — Add validation helpers (recommended starter coding task)

**Goal:** reject obviously bad inputs (year range, email format, allowed statuses).

**Where to add code:**

- Add helpers near the top of `src/filedb/cli.py` (below imports, above command functions).
- Call them inside `cmd_add_book` and `cmd_add_member`.

**Example code to add (in `cli.py`):**

```python
import re
from datetime import date

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def require_year(year: int) -> None:
    current = date.today().year
    if year < 1400 or year > current:
        raise SystemExit(f"Invalid year: {year}. Expected 1400..{current}.")

def require_email(email: str) -> None:
    if not _EMAIL_RE.match(email):
        raise SystemExit(f"Invalid email: {email}")

def require_one_of(value: str, allowed: set[str], field: str) -> None:
    v = (value or "").upper()
    if v not in allowed:
        raise SystemExit(f"Invalid {field}: {value}. Allowed: {sorted(allowed)}")
```

**Where to call it:**

- In `cmd_add_book(args)`, before writing:

```python
require_year(args.year)
```

- In `cmd_add_member(args)`, before writing:

```python
require_email(args.email)
```

**Why this exists in pre-DB systems:** clerks had procedures (“don’t accept forms without X”). Here, validation is your “procedure enforcement.”

---

### Extra Task 2 — Add a report command (inventory report)

**Goal:** add a pre-DB “report” command, e.g. counts by status and top authors.

**Where to add code:**

1. Add a new function to `src/filedb/cli.py`:
   - place it near other command functions, e.g. below `cmd_overdue`
2. Register it in `build_parser()` (add a new subparser)

**Example command function (add to `cli.py`):**

```python
def cmd_report_inventory(args: argparse.Namespace) -> int:
    books_path = path_for(args.data_dir, BOOKS_CSV)
    rows = read_csv_dicts(books_path)

    by_status: dict[str, int] = {}
    by_author: dict[str, int] = {}

    for r in rows:
        status = (r.get("status") or "").upper()
        author = (r.get("author") or "").strip()
        by_status[status] = by_status.get(status, 0) + 1
        by_author[author] = by_author.get(author, 0) + 1

    print("Books by status:")
    for k in sorted(by_status):
        print(f"  {k}: {by_status[k]}")

    print("\nTop authors:")
    top = sorted(by_author.items(), key=lambda kv: kv[1], reverse=True)[:10]
    for author, count in top:
        print(f"  {author}: {count}")
    return 0
```

**Register it in `build_parser()` (near other subcommands):**

```python
s = sub.add_parser("report-inventory", help="Report counts of books by status and top authors")
s.set_defaults(func=cmd_report_inventory)
```

---

### Extra Task 3 — Add a “verify-data” batch job (overnight scan)

**Goal:** scan all files, detect broken references and impossible states.

**Where to add code:**

- Add `cmd_verify_data` to `cli.py`
- Register it in `build_parser()`

**Example batch job (add to `cli.py`):**

```python
def cmd_verify_data(args: argparse.Namespace) -> int:
    books = read_csv_dicts(path_for(args.data_dir, BOOKS_CSV))
    members = read_csv_dicts(path_for(args.data_dir, MEMBERS_CSV))
    loans = read_csv_dicts(path_for(args.data_dir, LOANS_CSV))

    book_ids = {b.get("id") for b in books}
    member_ids = {m.get("id") for m in members}

    problems = 0

    for loan in loans:
        lid = loan.get("id")
        if loan.get("book_id") not in book_ids:
            print(f"[BROKEN] loan {lid}: missing book_id={loan.get('book_id')}")
            problems += 1
        if loan.get("member_id") not in member_ids:
            print(f"[BROKEN] loan {lid}: missing member_id={loan.get('member_id')}")
            problems += 1

        status = (loan.get("status") or "").upper()
        rdate = (loan.get("return_date") or "").strip()
        if status == "RETURNED" and rdate == "":
            print(f"[IMPOSSIBLE] loan {lid}: RETURNED but return_date empty")
            problems += 1
        if status == "OUT" and rdate != "":
            print(f"[IMPOSSIBLE] loan {lid}: OUT but return_date set")
            problems += 1

    print(f"Verify complete. Problems found: {problems}")
    return 0 if problems == 0 else 2
```

**Register it in `build_parser()`:**

```python
s = sub.add_parser("verify-data", help="Batch job: scan files and report data problems")
s.set_defaults(func=cmd_verify_data)
```

---

### Extra Task 4 — Demonstrate race conditions on IDs (two clerks)

**Goal:** make the problem obvious by inserting a small delay.

**Where to add code:**

- In `src/filedb/storage.py`, inside `next_id_naive`
- (Optional) only sleep if an env var is set

**Example code (in `storage.py`):**

```python
import time
import os

def next_id_naive(rows: List[Dict[str, str]]) -> int:
    if os.environ.get("FILEDB_SLOW_ID") == "1":
        time.sleep(0.2)
    # compute max(id)+1 as before...
```

Then run in two terminals:

```bash
FILEDB_SLOW_ID=1 python -m src.filedb add-member --name "Clerk A" --email "a@example.com"
FILEDB_SLOW_ID=1 python -m src.filedb add-member --name "Clerk B" --email "b@example.com"
```

---

## Deliverables

### Required (no coding)

- A short report covering Required Tasks 1–4:
  - how the ledgers work
  - which operations rewrite which files
  - what failure modes exist (crash, partial writes, inconsistencies)
  - your “binder rules” (procedures)

### Optional (extra credit / extension)

- Any implemented extras (validation, reports, verify-data batch job, etc.)
- Include screenshots / example runs showing the feature and the tradeoffs

---

## Hints

- If you keep adding “fixes” (lock files, indexes, logs, compaction), you will/would gradually reinvent a database.
- That’s the point. Document each fix and the new problems it introduces.
- Your system is allowed to be slow and fragile — just _show it_ and explain why.
