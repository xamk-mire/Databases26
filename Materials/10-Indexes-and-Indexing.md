# Indexes and Indexing

### Making queries faster (and understanding the trade-offs)

In [Materials 05](./Materials/05-SQL-fundamentals.md)–[07](./Materials/07-SQL-fundamentals-3.md) we created tables and wrote queries.  
In [Materials 09](./Materials/09-Transactions-and-Data-Modification.md) we focused on data changes and transactions.

This chapter introduces **indexes**:

- **What indexes are** — and why they help
- **When indexes help (and when they don’t)** — selectivity and access patterns
- **Index types and design** — primary, unique, composite, and order
- **Costs and trade-offs** — writes, storage, and maintenance

Examples use the same **university database** as earlier materials: `students`, `courses`, `enrollments`, `grades`, `teachers`.

---

# 1) What is an index?

An **index** is a separate data structure the database maintains to **find rows faster**.  
You can think of it like the index in a book: instead of scanning every page, you jump to the pages you need.

At a high level, an index stores:

- **Index keys** (values from one or more columns)
- **Pointers** to the actual table rows (so the database can jump directly to them)

Most PostgreSQL indexes are **B-tree** indexes, which keep the keys in sorted order and allow fast lookups, range searches, and ordered scans.

---

## How indexes exist in the database

An index is a **separate object** stored on disk, just like a table. It has its own name, storage, and structure.  
When you create an index, the database:

1. **Reads the table** and builds the index structure (keys + pointers)
2. **Stores the index** on disk
3. **Keeps it updated** whenever you `INSERT`, `UPDATE`, or `DELETE` rows

So every row change affects both the **table** and its **indexes**.

---

## How the database uses an index

When a query runs, the optimizer decides whether to use an index:

- **Sequential scan (Seq Scan):** read every row and filter
- **Index scan:** use the index to jump to matching rows

The choice depends on table size, selectivity, and statistics. For small tables or low‑selectivity columns, a sequential scan can be faster.

Indexes do **not** change query results; they only change **how** the database finds the rows.

---

## Example: Looking up a student by email

Query:

```sql
SELECT * FROM students WHERE email = 'aino@uni.fi';
```

If `students.email` is indexed, the database can go directly to the matching row.  
If not, it may scan the whole `students` table.

---

# 2) When indexes help (and when they don’t)

Indexes are great for **selective** queries — those that return a small fraction of rows.

They are less useful when:

- The column has **low selectivity** (many rows share the same value)
- The table is **tiny** (a scan is already cheap)
- The query doesn’t filter by the indexed column

They can also be less useful when the query returns **most of the table**. In that case, scanning the table once can be faster than jumping in and out via the index.

---

## Selectivity example

- `students.email` — usually unique → **high selectivity** → great index candidate.
- `grades.grade` — only values 0–5 → **low selectivity** → index may not help much.

---

# 3) Types of indexes you will use most

Most PostgreSQL indexes are **B-tree** indexes, which work well for:

- Equality lookups: `WHERE email = ...`
- Range queries: `WHERE grade BETWEEN 3 AND 5`
- Sorting: `ORDER BY full_name`

You don’t need to choose B-tree explicitly; it’s the default.

Other index types exist (e.g. hash, GIN, GiST), but they are used for special cases. For databases basics, B-tree covers most needs.

---

## Primary key and unique indexes

When you define a **PRIMARY KEY**, PostgreSQL automatically creates a unique index.  
Same for **UNIQUE** constraints.

Example:

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);
```

This creates:

- An index on `student_id` (primary key)
- A unique index on `email`

Unique indexes serve two purposes:

- **Speed** for lookups on that column
- **Data integrity** by enforcing uniqueness

---

# 4) Creating and dropping indexes

You can create an index on any column you query often.

### Create a simple index

```sql
CREATE INDEX idx_students_full_name ON students (full_name);
```

### Drop an index

```sql
DROP INDEX idx_students_full_name;
```

Index names should be descriptive, e.g. `idx_table_column` or `uq_table_column`.

---

# 5) Composite (multi-column) indexes

A **composite index** includes multiple columns. It helps when queries filter on **the leftmost columns** in the index.

Example index:

```sql
CREATE INDEX idx_grades_student_course ON grades (student_id, course_id);
```

This index is useful for:

- `WHERE student_id = 3 AND course_id = 1`
- `WHERE student_id = 3`

But it is **not** helpful for:

- `WHERE course_id = 1` (because `course_id` is not the leftmost column)

---

## Order matters

When designing composite indexes, put the **most selective** or **most common filter** first.

If most queries filter by `student_id`, then `(student_id, course_id)` is correct.  
If most queries filter by `course_id`, then `(course_id, student_id)` is better.

---

# 6) Indexes and ORDER BY

Indexes can speed up sorting if the sort order matches the index.

Example:

```sql
CREATE INDEX idx_courses_title ON courses (title);
```

Then:

```sql
SELECT title FROM courses ORDER BY title;
```

can use the index to avoid an extra sort step.

---

# 7) Costs and trade-offs

Indexes speed up reads, but they cost:

- **Write overhead** — every `INSERT`, `UPDATE`, and `DELETE` must also update indexes.
- **Storage** — indexes take extra disk space.
- **Maintenance** — too many indexes can slow down data changes.

So avoid indexing everything. Index **where it helps**.

---

## Good index candidates

- Columns used frequently in `WHERE`
- Columns used in `JOIN` conditions
- Columns used in `ORDER BY`
- Foreign keys on large tables (often helpful for joins)

---

# 8) Beyond the basics

These are common index ideas you will see in practice.

---

## Covering / index-only scans

If a query can be answered **entirely from the index**, PostgreSQL can sometimes avoid reading the table (heap) at all. This is called an **index-only scan**.

Example:

```sql
CREATE INDEX idx_students_email_name ON students (email, full_name);

SELECT email, full_name
FROM students
WHERE email LIKE '%@uni.fi';
```

If the needed columns are in the index, PostgreSQL can use the index to answer the query more efficiently.

---

## Partial indexes

A **partial index** stores only rows that match a condition. This can be smaller and faster when you always query a subset.

Example: only index students with an email:

```sql
CREATE INDEX idx_students_email_not_null
ON students (email)
WHERE email IS NOT NULL;
```

Queries that include `WHERE email IS NOT NULL` can use the index; others cannot.

---

## Functional indexes

If queries use a function in the WHERE clause, a normal index may not be used. A **functional index** can help.

Example: case-insensitive search for email:

```sql
CREATE INDEX idx_students_email_lower
ON students (LOWER(email));

SELECT * FROM students WHERE LOWER(email) = 'aino@uni.fi';
```

---

# 9) How to check if an index is used

PostgreSQL can show you a query plan with:

```sql
EXPLAIN SELECT * FROM students WHERE email = 'aino@uni.fi';
```

If you see **Index Scan**, the index is being used.  
If you see **Seq Scan**, the database chose a sequential scan.

Use `EXPLAIN` for learning and debugging; for real performance analysis you would use `EXPLAIN ANALYZE`.

You can compare two versions of the same query before and after creating an index to see the planner change its choice.

---

## EXPLAIN in practice

`EXPLAIN` shows the **query plan** — the steps PostgreSQL will use to execute your query. It does **not** run the query.

### Basic usage

```sql
EXPLAIN
SELECT s.full_name, c.title
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c ON c.course_id = e.course_id
WHERE s.student_id = 1;
```

### What to look for

- **Seq Scan** — PostgreSQL scans the whole table.
- **Index Scan / Index Only Scan** — PostgreSQL uses an index.
- **Join type** (e.g. Nested Loop, Hash Join) — how tables are combined.

### EXPLAIN ANALYZE (runs the query)

`EXPLAIN ANALYZE` **executes** the query and reports actual timings and row counts:

```sql
EXPLAIN ANALYZE
SELECT * FROM students WHERE email = 'aino@uni.fi';
```

Use it when you want real performance data, but be careful on large tables.

---

## Summary

| Topic               | Key ideas                                                                        |
| ------------------- | -------------------------------------------------------------------------------- |
| **Index**           | Separate data structure to speed up lookups and sorting.                         |
| **When it helps**   | High selectivity, frequent filters, joins, sorting.                              |
| **When it doesn’t** | Low selectivity, tiny tables, wrong access pattern.                              |
| **Composite index** | Order matters; leftmost columns are most useful.                                 |
| **Advanced basics** | Covering/index-only, partial, and functional indexes can help specific patterns. |
| **Trade-offs**      | Faster reads vs. slower writes and more storage.                                 |

---

_End of Materials 10._
