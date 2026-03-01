# Exercise 4: Normalization, Transactions & Data Modification

### Winter Olympics — from bad design to 3NF, then practice data changes

> **Instructions:**  
> You are given a **badly designed** Winter Olympics database (one denormalized table). You will **analyse** it, **normalize** it to 3NF, **migrate** the data, then practice UPDATE, DELETE, transactions, and rollbacks on the normalized database. Refer to [Materials 08 — Normalization and Schema Quality](../../Materials/08-Normalization-and-Schema-Quality.md) and [Materials 09 — Transactions and Data Modification](../../Materials/09-Transactions-and-Data-Modification.md) as needed.
>
> **Setup (do this first):** Create a new PostgreSQL database **`winter_olympics`**, then run **`04_bad_schema.sql`** and **`04_bad_seed.sql`**. You will have one table, **`medal_results`**, with redundant data.

---

## The bad design you start with

After running `04_bad_schema.sql` and `04_bad_seed.sql`, you have a single table:

**`medal_results`** — one row per athlete per event (one medal), with columns:

| Column       | Description (redundant in many rows)                |
| ------------ | --------------------------------------------------- |
| athlete_id   | Athlete identifier                                  |
| athlete_name | Repeated for every result of that athlete           |
| country_code | Repeated for every result of that athlete           |
| country_name | Repeated for every result of that athlete           |
| event_id     | Event identifier                                    |
| event_name   | Repeated for every result in that event             |
| sport_name   | Repeated for every result in that event             |
| venue_name   | Repeated for every result at that venue             |
| city         | Repeated for every result at that venue             |
| medal_type   | gold / silver / bronze (depends on athlete + event) |

Run `SELECT * FROM medal_results;` to see the data and the repetition.

---

## PART A — Analyse the bad design (Materials 08)

Answer the following about the **`medal_results`** table. Use the table structure above and the data you see in the database.

---

### A1 — Redundancy and anomalies

**A1.1** **Update anomaly** — If Mika Virtanen’s name is corrected (e.g. spelling), what must happen in this design? What goes wrong if we update only one row?

_Your answer:_

If Mika Virtanen’s name is corrected, it must be updated in every row where he appears. If we update only one row, the database will contain inconsistent data (some rows with the old name, some with the corrected name).

**A1.2** **Insert anomaly** — We want to add a new event "Team Relay" in Cross-Country Skiing, at Mountain Resort, Zhangjiakou, before any athlete has competed in it. Can we do it with this single table? Explain briefly.

_Your answer:_

No, we cannot add the new event without inserting an athlete and medal result, because the table stores everything in one row. This design prevents inserting an event independently of a result.

**A1.3** **Delete anomaly** — If we delete the row for Sara Niemi in Women’s Slalom, what information do we lose beyond that one medal result?

_Your answer:_

If we delete the row for Sara Niemi in Women’s Slalom, we also lose the event information, sport name, venue name, city, and country information if they appear only in that row.

### A2 — First Normal Form (1NF)

The `medal_results` table has atomic values in each cell and a primary key `(athlete_id, event_id)`.

**A2.1** Is this table in 1NF? (Yes/No and one sentence why.)

_Your answer:_

Yes. Each column contains atomic values and the table has a defined primary key.

**A2.2** Suppose instead we had a column `events_won` storing multiple values in one cell, e.g. `"Men's Downhill, Men's 50km"`. Why would that **not** be 1NF?

_Your answer:_

Because a single column would contain multiple values in one cell, which violates the requirement that each field must contain only one atomic value.
### A3 — Second Normal Form (2NF)

The primary key of `medal_results` is **composite**: `(athlete_id, event_id)`.

**A3.1** Which attribute(s) depend **only** on `athlete_id`? Which depend **only** on `event_id`? Which depend on **both** (the full key)?

_Your answer:_

Depends only on athlete_id:

athlete_name

country_code

country_name

Depends only on event_id:

event_name

sport_name

venue_name

city

Depends on both (full key):

medal_type
**A3.2** So does `medal_results` satisfy 2NF? (Yes/No and one sentence.)

_Your answer:_

No. The table does not satisfy 2NF because there are partial dependencies on parts of the composite primary key.

**A3.3** To achieve 2NF, we split into separate tables. List the **tables** you would have and each table’s **primary key**. (You will implement these in Part B.)

_Your answer:_

To achieve 2NF, we split into these tables:

countries (country_id PRIMARY KEY)

athletes (athlete_id PRIMARY KEY)

sports (sport_id PRIMARY KEY)

venues (venue_id PRIMARY KEY)

events (event_id PRIMARY KEY)

results (PRIMARY KEY (athlete_id, event_id))

### A4 — Third Normal Form (3NF)

Suppose we had split events into a table **`events(event_id, event_name, sport_id, venue_name, city)`** — i.e. we still store venue name and city inside the events table.

**A4.1** What **transitive dependency** exists there? (Which non-key attribute depends on another non-key attribute?)

_Your answer:_

There is a transitive dependency where city depends on venue_name (a non-key attribute depends on another non-key attribute).

**A4.2** How do we fix it to satisfy 3NF? (Name the tables: e.g. one for venues, one for events with only venue_id.)

_Your answer:_

We fix it by creating a separate venues table:

venues (venue_id, venue_name, city)

events (event_id, event_name, sport_id, venue_id)

This removes the transitive dependency.

### A5 — When denormalization might be acceptable (short)

Give **one** situation where denormalization is sometimes used despite the risk of redundancy.

_Your answer:_

Denormalization is sometimes used in reporting or analytics systems to improve query performance and reduce complex joins.

## PART B — Normalize to 3NF using transactions

Your task is to **design and implement** the normalized schema yourself: write the `CREATE TABLE` statements, then **migrate** data from `medal_results` into the new tables. You must use **transactions** so that the normalization is safe: if any step fails, you can **ROLLBACK** and the database stays consistent. Only **COMMIT** when you have verified the migration.

**Important:** No ready-made normalized schema or migration script is provided. You write them based on your Part A design (A3.3 and A4.2). Use [Materials 07](07-SQL-fundamentals-3.md) for foreign key and constraint syntax, and [Materials 09](09-Transactions-and-Data-Modification.md) for transactions.

---

### B1 — Design and create the normalized schema (in a transaction)

**B1.1** Write `CREATE TABLE` statements for all 3NF tables: **countries**, **athletes**, **sports**, **venues**, **events**, **results**. Include primary keys, foreign keys where needed, and constraints (e.g. `CHECK (medal_type IN ('gold', 'silver', 'bronze'))` for results). For identity columns use `GENERATED ALWAYS AS IDENTITY`. Add an **email** column (nullable) to **athletes** for later exercises. Do **not** drop `medal_results` — you need it for migration.

Run your CREATE statements **inside a transaction**: `BEGIN;` … your CREATE TABLEs … `COMMIT;` If anything fails, fix the SQL and try again. In PostgreSQL, DDL is transactional, so either all tables are created or none are.

```sql
BEGIN;

CREATE TABLE countries (
    country_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code TEXT UNIQUE NOT NULL,
    country_name TEXT NOT NULL
);

CREATE TABLE athletes (
    athlete_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name TEXT NOT NULL,
    country_id INTEGER REFERENCES countries(country_id),
    email TEXT
);

CREATE TABLE sports (
    sport_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sport_name TEXT UNIQUE NOT NULL
);

CREATE TABLE venues (
    venue_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venue_name TEXT NOT NULL,
    city TEXT NOT NULL
);

CREATE TABLE events (
    event_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_name TEXT NOT NULL,
    sport_id INTEGER REFERENCES sports(sport_id),
    venue_id INTEGER REFERENCES venues(venue_id)
);

CREATE TABLE results (
    athlete_id INTEGER REFERENCES athletes(athlete_id),
    event_id INTEGER REFERENCES events(event_id),
    medal_type TEXT CHECK (medal_type IN ('gold','silver','bronze')),
    PRIMARY KEY (athlete_id, event_id)
);

COMMIT;

---

**B1.2** In the normalized design, why does **events** have `venue_id` (a foreign key) instead of `venue_name` and `city`? One sentence.

_Your answer:_

Because venue is a separate entity, and city depends on venue, so events should store only venue_id as a foreign key instead of repeating venue_name and city.
### B2 — Migrate data using a transaction

Copy data from `medal_results` into the new tables in **dependency order**:

1. **countries** — distinct `(country_code, country_name)` from `medal_results`
2. **athletes** — distinct `(athlete_id, athlete_name, country_code)`; you need `country_id` from **countries** (join on `country_code`). To keep the same `athlete_id` values for the **results** table, use `INSERT INTO athletes (athlete_id, full_name, country_id) OVERRIDING SYSTEM VALUE SELECT ...`
3. **sports** — distinct `sport_name`
4. **venues** — distinct `(venue_name, city)`
5. **events** — distinct `(event_id, event_name, sport_name, venue_name, city)`; join to **sports** and **venues** to get `sport_id` and `venue_id`. Use `OVERRIDING SYSTEM VALUE` for `event_id` so it matches the values in `medal_results`
6. **results** — `SELECT athlete_id, event_id, medal_type FROM medal_results`

**B2.1** Run the entire migration **inside one transaction**: `BEGIN;` then all your `INSERT ... SELECT` statements in the order above, then **verify** with e.g. `SELECT COUNT(*) FROM results;` (expect 8) and `SELECT COUNT(*) FROM athletes;` (expect 6). Only then run **COMMIT;**. If any INSERT fails or counts are wrong, run **ROLLBACK;** fix your SQL, and try again.

Write your migration (all INSERTs) in the block below. Use one transaction for the whole migration.

```sql
BEGIN;

-- 1. Countries
INSERT INTO countries (country_code, country_name)
SELECT DISTINCT country_code, country_name
FROM medal_results;

-- 2. Athletes
INSERT INTO athletes (athlete_id, full_name, country_id)
OVERRIDING SYSTEM VALUE
SELECT DISTINCT m.athlete_id,
       m.athlete_name,
       c.country_id
FROM medal_results m
JOIN countries c ON m.country_code = c.country_code;

-- 3. Sports
INSERT INTO sports (sport_name)
SELECT DISTINCT sport_name
FROM medal_results;

-- 4. Venues
INSERT INTO venues (venue_name, city)
SELECT DISTINCT venue_name, city
FROM medal_results;

-- 5. Events
INSERT INTO events (event_id, event_name, sport_id, venue_id)
OVERRIDING SYSTEM VALUE
SELECT DISTINCT m.event_id,
       m.event_name,
       s.sport_id,
       v.venue_id
FROM medal_results m
JOIN sports s ON m.sport_name = s.sport_name
JOIN venues v ON m.venue_name = v.venue_name
             AND m.city = v.city;

-- 6. Results
INSERT INTO results (athlete_id, event_id, medal_type)
SELECT athlete_id, event_id, medal_type
FROM medal_results;

-- Verification
SELECT COUNT(*) FROM results;   -- should be 8
SELECT COUNT(*) FROM athletes;  -- should be 6

COMMIT;
```

---

**B2.2** Why is it important to run the migration inside a transaction? One sentence.

_Your answer:_

Because if any step fails, the entire migration can be rolled back, keeping the database consistent.
### B3 — Drop the old table (in a transaction)

**B3.1** Once the migration is committed and you have verified the data (e.g. 8 rows in **results**, 6 in **athletes**), drop the old table. Do it in a transaction: `BEGIN; DROP TABLE medal_results; COMMIT;` so that if something else depends on it, you can ROLLBACK.

```sql
BEGIN;
DROP TABLE medal_results;
COMMIT;
```

After this, you will use only the normalized tables for Part C.

---

## PART C — Data modification on the normalized database (Materials 09)

Use the **normalized** Winter Olympics database (countries, athletes, sports, venues, events, results). Run your SQL in **psql** or pgAdmin.

---

### C1 — UPDATE

**C1.1** Add or update the email of the athlete with `athlete_id = 2` (Sara Niemi) to `sara.niemi@olympics.fi`. Use a `WHERE` clause on `athlete_id`.

_Self-check: `SELECT full_name, email FROM athletes WHERE athlete_id = 2;` shows the new email._

```sql
UPDATE athletes
SET email = 'sara.niemi@olympics.fi'
WHERE athlete_id = 2;

```

---

**C1.2** Update **all** events that use `venue_id = 1` so they use `venue_id = 3` instead. Use `WHERE venue_id = 1`.

_Self-check: No event should have venue_id = 1 after the update._

```sql
UPDATE events
SET venue_id = 3
WHERE venue_id = 1;

```

---

**C1.3** (Safety) Before running any UPDATE that affects multiple rows, what should you do first? One sentence.

_Your answer:_

Before running an UPDATE affecting multiple rows, we should first run a SELECT with the same WHERE clause to verify which rows will be affected.

### C2 — DELETE

**C2.1** Delete **one** result: the row where `athlete_id = 5` and `event_id = 5` (James Chen, Pairs Figure Skating). Use a `WHERE` with both columns.

_Self-check: `SELECT _ FROM results;` should have 7 rows.\*

```sql
DELETE FROM results
WHERE athlete_id = 5 AND event_id = 5;

```

---

**C2.2** If we wanted to delete all results for athlete 3, we would run `DELETE FROM results WHERE athlete_id = 3;`. Before doing that, what should we run first and why?

_Your answer:_

We should first run a SELECT with the same WHERE clause to see which rows will be deleted and avoid accidental data loss.
### C3 — Transactions (BEGIN, COMMIT)

**C3.1** Use a **transaction** to do two things together:

1. Insert a new athlete: `full_name = 'Liisa Korhonen'`, `country_id = 1` (Finland), `email = NULL`.
2. Insert a new result for that athlete in `event_id = 4` (Women's Sprint) with `medal_type = 'bronze'`.

You need the new `athlete_id` for the result row (e.g. use `RETURNING athlete_id` or `currval(pg_get_serial_sequence('athletes','athlete_id'))` after the first INSERT). Use `BEGIN;` before the INSERTs and `COMMIT;` after.

```sql
BEGIN;

INSERT INTO athletes (full_name, country_id, email)
VALUES ('Liisa Korhonen', 1, NULL)
RETURNING athlete_id;

-- Assume returned athlete_id = 7

INSERT INTO results (athlete_id, event_id, medal_type)
VALUES (7, 4, 'bronze');

COMMIT;
```

---

**C3.2** In one sentence: why is it useful to put these two INSERTs in a single transaction?

_Your answer:_

Because both inserts must succeed together; otherwise, we would have incomplete or inconsistent data.

### C4 — Rollback

**C4.1** Start a transaction, update an athlete’s email to a test value (e.g. `'rollback_test@test.com'` for `athlete_id = 1`), then run **ROLLBACK;** instead of COMMIT. After that, run `SELECT email FROM athletes WHERE athlete_id = 1;` — the email should be unchanged. Write the statements you ran.

```sql
BEGIN;

UPDATE athletes
SET email = 'rollback_test@test.com'
WHERE athlete_id = 1;

ROLLBACK;
```

---

**C4.2** In one sentence: what does ROLLBACK do to the changes made since the last BEGIN?

_Your answer:_

ROLLBACK cancels all changes made since the last BEGIN and restores the database to its previous state.

## Self-check (validation)

Before finishing, confirm:

1. **Part A:** You identified update, insert, and delete anomalies; partial dependencies (2NF); transitive dependency (3NF).
2. **Part B:** You wrote and ran your own CREATE TABLE statements in a transaction; you wrote and ran your own migration (INSERT...SELECT) in a transaction and verified row counts before COMMIT; you dropped `medal_results` in a transaction. Final state: 8 rows in **results**, 6 in **athletes**.
3. **Part C:** C1.1 and C1.2 applied; C2.1 deleted one result; C3 ran two INSERTs in one transaction; C4 rollback left athlete 1’s email unchanged.

---

## Files in this exercise

| File                  | Purpose                                                        |
| --------------------- | -------------------------------------------------------------- |
| **Instructions.md**   | This document                                                  |
| **04_bad_schema.sql** | Creates the bad design (one table `medal_results`) — run first |
| **04_bad_seed.sql**   | Sample data for `medal_results` — run second                   |

You will write your normalized schema (CREATE TABLE) and migration (INSERT...SELECT) yourself, using transactions as described in Part B.

---

_End of Exercise 4._
