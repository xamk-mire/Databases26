# Transactions and Data Modification

### UPDATE, DELETE, transactions, ACID, and isolation

In [Materials 05](05-SQL-fundamentals.md)–[07](07-SQL-fundamentals-3.md) we used `INSERT` and `SELECT` to add and read data.  
In [Materials 08](08-Normalization-and-Schema-Quality.md) we looked at schema quality and normalization.

This chapter focuses on **changing and removing data** and **controlling how changes are applied**:

- **UPDATE and DELETE** — Modifying and removing rows
- **Transactions** — Grouping statements so they succeed or fail together
- **ACID properties** — What the database guarantees
- **Rollbacks** — Undoing work within a transaction

This chapter uses the same **university database** as in [Materials 05](05-SQL-fundamentals.md)–[07](07-SQL-fundamentals-3.md): `students`, `courses`, `enrollments`, `grades`, `teachers`.

---

## Shared example schema (reminder)

### Table: `students`

| student_id | full_name     | email          |
| ---------: | ------------- | -------------- |
|          1 | Aino Laine    | aino@uni.fi    |
|          2 | Mika Virtanen | mika@uni.fi    |
|          3 | Sara Niemi    | _(NULL)_       |
|          4 | Olli Koski    | olli@gmail.com |

### Table: `teachers`

| teacher_id | full_name      | email        |
| ---------: | -------------- | ------------ |
|          1 | Liisa Korhonen | liisa@uni.fi |
|          2 | Pekka Salo     | pekka@uni.fi |
|          3 | Maria Lind     | maria@uni.fi |

### Table: `courses`

| course_id | title           | credits | teacher_id |
| --------: | --------------- | ------: | ---------: |
|         1 | Databases       |       5 |          1 |
|         2 | Algorithms      |       6 |          2 |
|         3 | Web Development |       5 |          3 |

### Table: `enrollments`

| student_id | course_id |
| ---------: | --------: |
|          1 |         1 |
|          1 |         2 |
|          2 |         1 |
|          3 |         1 |
|          3 |         3 |
|          4 |         3 |

### Table: `grades`

| student_id | course_id | grade |
| ---------: | --------: | ----: |
|          1 |         1 |     5 |
|          1 |         2 |     4 |
|          2 |         1 |     3 |
|          3 |         1 |     2 |
|          3 |         3 |     5 |
|          4 |         3 |     4 |

---

# 1) UPDATE and DELETE

Besides `INSERT` and `SELECT`, the main data-modification statements are **UPDATE** (change existing rows) and **DELETE** (remove rows). Both use a **WHERE** clause to choose which rows are affected.

---

## UPDATE — Change existing rows

**Syntax (simplified):**

```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

- **SET** — Which columns to change and to what value(s).
- **WHERE** — Which rows to update. **If you omit WHERE, every row in the table is updated.**

### Example: Update one student’s email

```sql
UPDATE students
SET email = 'aino.new@uni.fi'
WHERE student_id = 1;
```

Only rows that match the condition are changed. Use a unique identifier (e.g. `student_id`) when possible so you don’t accidentally update multiple rows.

### Example: Update several rows

```sql
UPDATE courses
SET credits = credits + 1
WHERE teacher_id = 1;
```

Here, every course taught by teacher 1 gets one extra credit (e.g. after a curriculum change).

### Safety tip

Always check **how many rows** your condition matches before updating. You can run a `SELECT` with the same `WHERE` first:

```sql
-- First: see which rows would be updated
SELECT * FROM students WHERE student_id = 1;

-- Then: run the UPDATE
UPDATE students SET email = 'aino.new@uni.fi' WHERE student_id = 1;
```

In PostgreSQL you can use `UPDATE ... RETURNING *` to see the updated rows after the statement.

---

## DELETE — Remove rows

**Syntax (simplified):**

```sql
DELETE FROM table_name
WHERE condition;
```

- **WHERE** — Which rows to delete. **If you omit/remove WHERE, every row in the table is deleted.**

### Example: Delete one enrollment

```sql
DELETE FROM enrollments
WHERE student_id = 3 AND course_id = 1;
```

### Example: Delete all enrollments for a student

```sql
DELETE FROM enrollments
WHERE student_id = 4;
```

(If you have `ON DELETE CASCADE` on `grades`, the database may also delete the related grade rows when you delete from `enrollments` only if the design links them that way; typically you would delete from `grades` first or use constraints as in [Materials 07](07-SQL-fundamentals-3.md).)

### Safety tip

Same as with UPDATE: run a `SELECT` with the same `WHERE` first to see which rows would be deleted. In PostgreSQL, `DELETE ... RETURNING *` shows the deleted rows.

---

## Summary: UPDATE and DELETE

| Statement  | Purpose              | Danger without WHERE |
| ---------- | -------------------- | -------------------- |
| **UPDATE** | Change column values | Updates **all** rows |
| **DELETE** | Remove rows          | Deletes **all** rows |

Always use a precise `WHERE` (preferably on primary key or unique column) unless you really intend to affect the whole table.

---

# 2) Transactions

A **transaction** is a group of one or more SQL statements that the database treats as a **single unit of work**: either **all** of them take effect, or **none** of them do.

---

## Why transactions matter

Without transactions, if one statement succeeds and the next fails, you can end up with half-done work (e.g. a student enrolled in a course but no grade row created). Transactions let you:

- **Commit** — Make all changes in the transaction permanent.
- **Roll back** — Cancel all changes in the transaction, as if they never happened.

---

## Explicit transactions in PostgreSQL

You control a transaction with:

- **BEGIN** (or **START TRANSACTION**) — Start a new transaction.
- **COMMIT** — End the transaction and make all changes permanent.
- **ROLLBACK** — End the transaction and discard all changes.

Everything between `BEGIN` and `COMMIT` (or `ROLLBACK`) is one transaction.

### Example: Two updates that must happen together

Suppose we want to swap the teachers for two courses. Both updates must succeed or neither should:

```sql
BEGIN;

UPDATE courses SET teacher_id = 2 WHERE course_id = 1;
UPDATE courses SET teacher_id = 1 WHERE course_id = 2;

COMMIT;
```

If you run `COMMIT`, both updates are applied. If you run `ROLLBACK` instead, neither update is applied.

### Example: Multiple inserts as one unit

When enrolling a student in a course, we might add both an enrollment and a placeholder grade. Both should be created together:

```sql
BEGIN;

INSERT INTO enrollments (student_id, course_id) VALUES (4, 2);
INSERT INTO grades (student_id, course_id, grade) VALUES (4, 2, NULL);

COMMIT;
```

(If `grades.grade` is defined as `NOT NULL`, use a placeholder like 0 or omit the grade row until the grade is set; adjust to your schema.) If the second `INSERT` fails (e.g. constraint violation), you can `ROLLBACK` so the student is not left enrolled without a grade row (or vice versa).

---

## Autocommit (default behaviour)

In most clients, each statement is automatically committed if you do not start a transaction. So a single `UPDATE` or `DELETE` is effectively a one-statement transaction: it commits immediately. To group several statements, you must use `BEGIN` ... `COMMIT` (or `ROLLBACK`).

---

# 3) ACID Properties

Databases that support transactions typically provide **ACID** guarantees:

| Property        | Meaning in plain terms                                                                                                                                                                                          |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Atomicity**   | The transaction is all-or-nothing: either every statement in it is applied, or none are. No “half commit.”                                                                                                      |
| **Consistency** | The database moves from one valid state to another. Constraints (e.g. foreign keys, CHECK) are enforced so data never violates the rules you defined.                                                           |
| **Isolation**   | Concurrent transactions do not see each other’s uncommitted changes in a way that breaks the guarantees of the isolation level (see below). So one transaction’s work is isolated from others until it commits. |
| **Durability**  | Once a transaction is committed, its changes are permanent even if the server crashes or loses power (they are stored on disk and recovered after restart).                                                     |

---

### Atomicity

If you `ROLLBACK` or the database aborts the transaction (e.g. after an error), **all** changes made in that transaction are undone. There is no partial commit.

### Consistency

The database ensures that after every committed transaction, all constraints hold. If a statement would violate a constraint, the statement fails and (unless you handle it) the transaction can be rolled back so the database stays in a valid state.

### Isolation

Two transactions running at the same time see a view of the data that depends on the **isolation level**. At higher levels, your transaction is more “shielded” from other transactions’ uncommitted or later changes; at lower levels, you might see more up-to-date or intermediate data. See [Section 5](#5-isolation-levels-introductory) below.

### Durability

After `COMMIT`, the database does not “forget” your changes on restart. They are written to durable storage (e.g. WAL and data files) and replayed during recovery.

---

# 4) Rollbacks

**Rollback** means ending a transaction by **discarding** all changes made in that transaction. The database restores the state to what it was at the start of the transaction (from your transaction’s point of view).

---

## Explicit ROLLBACK

You can explicitly roll back by running:

```sql
ROLLBACK;
```

Everything since the last `BEGIN` is undone. No rows are updated, inserted, or deleted by that transaction.

### Example

```sql
BEGIN;
UPDATE students SET email = 'test@test.com' WHERE student_id = 1;
-- You change your mind:
ROLLBACK;
```

The email is not changed; the transaction ends without making any persistent changes.

---

## Automatic rollback on error

If a statement inside a transaction **fails** (e.g. constraint violation, syntax error), the database marks the transaction as aborted. Subsequent statements in the same transaction will fail until you either:

- **ROLLBACK** — Discard the transaction and start over, or
- **COMMIT** — In many systems, `COMMIT` after an error will effectively roll back the transaction (no changes are committed).

So in practice, after an error you typically issue `ROLLBACK` and then retry or fix the logic.

---

## Savepoints (optional)

PostgreSQL (and others) support **savepoints** inside a transaction: you can roll back to a named point without rolling back the whole transaction.

```sql
BEGIN;
UPDATE courses SET credits = 6 WHERE course_id = 1;
SAVEPOINT before_second_change;
UPDATE courses SET credits = 4 WHERE course_id = 2;
-- If something is wrong:
ROLLBACK TO SAVEPOINT before_second_change;
-- First UPDATE is still in the transaction; second is undone.
COMMIT;
```

This is useful for “partial undo” within one transaction. An introductory course can skip savepoints and use only `BEGIN` / `COMMIT` / `ROLLBACK`.

---

## Summary

| Topic            | Key ideas                                                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **UPDATE**       | Change column values; use WHERE to limit rows. Without WHERE, all rows are updated.                                                            |
| **DELETE**       | Remove rows; use WHERE to limit rows. Without WHERE, all rows are deleted.                                                                     |
| **Transactions** | BEGIN … COMMIT (or ROLLBACK) group statements into one unit of work. All or nothing.                                                           |
| **ACID**         | Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions), Durability (committed data survives crashes). |
| **Rollbacks**    | ROLLBACK discards all changes in the current transaction. Errors typically abort the transaction; you then ROLLBACK and retry.                 |

---

_End of Materials 09._
