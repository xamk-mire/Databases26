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

---

**A1.2** **Insert anomaly** — We want to add a new event "Team Relay" in Cross-Country Skiing, at Mountain Resort, Zhangjiakou, before any athlete has competed in it. Can we do it with this single table? Explain briefly.

_Your answer:_

---

**A1.3** **Delete anomaly** — If we delete the row for Sara Niemi in Women’s Slalom, what information do we lose beyond that one medal result?

_Your answer:_

---

### A2 — First Normal Form (1NF)

The `medal_results` table has atomic values in each cell and a primary key `(athlete_id, event_id)`.

**A2.1** Is this table in 1NF? (Yes/No and one sentence why.)

_Your answer:_

---

**A2.2** Suppose instead we had a column `events_won` storing multiple values in one cell, e.g. `"Men's Downhill, Men's 50km"`. Why would that **not** be 1NF?

_Your answer:_

---

### A3 — Second Normal Form (2NF)

The primary key of `medal_results` is **composite**: `(athlete_id, event_id)`.

**A3.1** Which attribute(s) depend **only** on `athlete_id`? Which depend **only** on `event_id`? Which depend on **both** (the full key)?

_Your answer:_

---

**A3.2** So does `medal_results` satisfy 2NF? (Yes/No and one sentence.)

_Your answer:_

---

**A3.3** To achieve 2NF, we split into separate tables. List the **tables** you would have and each table’s **primary key**. (You will implement these in Part B.)

_Your answer:_

---

### A4 — Third Normal Form (3NF)

Suppose we had split events into a table **`events(event_id, event_name, sport_id, venue_name, city)`** — i.e. we still store venue name and city inside the events table.

**A4.1** What **transitive dependency** exists there? (Which non-key attribute depends on another non-key attribute?)

_Your answer:_

---

**A4.2** How do we fix it to satisfy 3NF? (Name the tables: e.g. one for venues, one for events with only venue_id.)

_Your answer:_

---

### A5 — When denormalization might be acceptable (short)

Give **one** situation where denormalization is sometimes used despite the risk of redundancy.

_Your answer:_

---

## PART B — Normalize to 3NF using transactions

Your task is to **design and implement** the normalized schema yourself: write the `CREATE TABLE` statements, then **migrate** data from `medal_results` into the new tables. You must use **transactions** so that the normalization is safe: if any step fails, you can **ROLLBACK** and the database stays consistent. Only **COMMIT** when you have verified the migration.

**Important:** No ready-made normalized schema or migration script is provided. You write them based on your Part A design (A3.3 and A4.2). Use [Materials 07](07-SQL-fundamentals-3.md) for foreign key and constraint syntax, and [Materials 09](09-Transactions-and-Data-Modification.md) for transactions.

---

### B1 — Design and create the normalized schema (in a transaction)

**B1.1** Write `CREATE TABLE` statements for all 3NF tables: **countries**, **athletes**, **sports**, **venues**, **events**, **results**. Include primary keys, foreign keys where needed, and constraints (e.g. `CHECK (medal_type IN ('gold', 'silver', 'bronze'))` for results). For identity columns use `GENERATED ALWAYS AS IDENTITY`. Add an **email** column (nullable) to **athletes** for later exercises. Do **not** drop `medal_results` — you need it for migration.

Run your CREATE statements **inside a transaction**: `BEGIN;` … your CREATE TABLEs … `COMMIT;` If anything fails, fix the SQL and try again. In PostgreSQL, DDL is transactional, so either all tables are created or none are.

```sql
BEGIN;

-- Your CREATE TABLE countries; ... CREATE TABLE results; here


COMMIT;
```

---

**B1.2** In the normalized design, why does **events** have `venue_id` (a foreign key) instead of `venue_name` and `city`? One sentence.

_Your answer:_

---

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

-- 1. INSERT INTO countries ...
-- 2. INSERT INTO athletes ... (use OVERRIDING SYSTEM VALUE for athlete_id)
-- 3. INSERT INTO sports ...
-- 4. INSERT INTO venues ...
-- 5. INSERT INTO events ... (use OVERRIDING SYSTEM VALUE for event_id, join to sports and venues)
-- 6. INSERT INTO results ...

-- Verify before COMMIT:
-- SELECT COUNT(*) FROM results;  -- should be 8
-- SELECT COUNT(*) FROM athletes;  -- should be 6

COMMIT;   -- or ROLLBACK; if something is wrong
```

---

**B2.2** Why is it important to run the migration inside a transaction? One sentence.

_Your answer:_

---

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


```

---

**C1.2** Update **all** events that use `venue_id = 1` so they use `venue_id = 3` instead. Use `WHERE venue_id = 1`.

_Self-check: No event should have venue_id = 1 after the update._

```sql


```

---

**C1.3** (Safety) Before running any UPDATE that affects multiple rows, what should you do first? One sentence.

_Your answer:_

---

### C2 — DELETE

**C2.1** Delete **one** result: the row where `athlete_id = 5` and `event_id = 5` (James Chen, Pairs Figure Skating). Use a `WHERE` with both columns.

_Self-check: `SELECT _ FROM results;` should have 7 rows.\*

```sql


```

---

**C2.2** If we wanted to delete all results for athlete 3, we would run `DELETE FROM results WHERE athlete_id = 3;`. Before doing that, what should we run first and why?

_Your answer:_

---

### C3 — Transactions (BEGIN, COMMIT)

**C3.1** Use a **transaction** to do two things together:

1. Insert a new athlete: `full_name = 'Liisa Korhonen'`, `country_id = 1` (Finland), `email = NULL`.
2. Insert a new result for that athlete in `event_id = 4` (Women's Sprint) with `medal_type = 'bronze'`.

You need the new `athlete_id` for the result row (e.g. use `RETURNING athlete_id` or `currval(pg_get_serial_sequence('athletes','athlete_id'))` after the first INSERT). Use `BEGIN;` before the INSERTs and `COMMIT;` after.

```sql
BEGIN;


COMMIT;
```

---

**C3.2** In one sentence: why is it useful to put these two INSERTs in a single transaction?

_Your answer:_

---

### C4 — Rollback

**C4.1** Start a transaction, update an athlete’s email to a test value (e.g. `'rollback_test@test.com'` for `athlete_id = 1`), then run **ROLLBACK;** instead of COMMIT. After that, run `SELECT email FROM athletes WHERE athlete_id = 1;` — the email should be unchanged. Write the statements you ran.

```sql
BEGIN;


ROLLBACK;
```

---

**C4.2** In one sentence: what does ROLLBACK do to the changes made since the last BEGIN?

_Your answer:_

---

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
