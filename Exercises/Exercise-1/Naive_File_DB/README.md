# File-based "Database" Starter (Python)

This starter project is intentionally **naïve**: it rewrites whole CSV files for updates, does full scans for reads,
and has no real transactional guarantees.

## What you get

- A small CLI (`python -m src.cli ...`) with stubbed commands
- CSV-backed storage helpers
- Dataclass "models"
- A minimal `data/` folder with example CSVs

## Setup

Requires Python 3.10+.

```bash
cd filedb_starter
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Folder layout

- `src/cli.py` — CLI entrypoint (argparse subcommands)
- `src/commands.py` — business logic for commands (validation, joins across files)
- `src/storage.py` — naive CSV storage helpers (read/write/append/update)
- `src/models.py` — small dataclasses + constants
- `data/` — example CSV files (books/members/loans)
- `scripts/generate_data.py` — data generator (scale to 100k+ rows)

## Quick start

### 1) Run a command

```bash
# show help
python -m src.cli --help

# create example data in ./data
python data/generate_data.py --books 50 --members 20 --loans 30 --out ./data

# add a member
python -m src.cli add-member --name "Ada Lovelace" --email "ada@example.com"

# add a book
python -m src.cli add-book --title "Dune" --author "Frank Herbert" --year 1965

# checkout + return
python -m src.cli checkout --book-id 1 --member-id 1
python -m src.cli return --loan-id 1

# search
python -m src.cli find-book --title dune
python -m src.cli member-loans --member-id 1
python -m src.cli overdue --days 14
```

## Exercise expectations (suggested)

Implement/improve the TODOs found in the code:

- ID generation that avoids collisions (then demonstrate why it's hard without locking/transactions)
- Validation (status values, required fields, dates)
- Business rules:
  - no checkout if book is already OUT
  - no checkout if member is SUSPENDED
  - reject loans with non-existent book/member ids
- Meaningful errors + exit codes
- (Pain lab) create a big dataset and time operations

## Key design constraints (on purpose)

- CSV is the single source of truth
- Updates rewrite the whole file (or require you to implement append-only + compaction)
- Searches are linear scans unless you add your own indexing

Have fun :smile:
