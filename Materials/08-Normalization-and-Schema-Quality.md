# Normalization and Schema Quality

### Reducing redundancy and structuring data well

In [Materials 03](03-Relational-Database.md) we introduced the relational model and tables.  
In [Materials 05](05-SQL-fundamentals.md)–[07](07-SQL-fundamentals-3.md) we built schemas with foreign keys and constraints.

This chapter focuses on **schema design quality**:

- **Redundancy problems** — Why duplicated data causes trouble
- **Normal forms (1NF, 2NF, 3NF)** — Standard rules for organizing tables
- **When denormalization is acceptable** — Trading purity for practical needs

No new SQL syntax; this is about *how* to structure tables so data stays consistent and maintainable.

---

# 1) Redundancy Problems

**Redundancy** means storing the same fact in more than one place. A little redundancy can be intentional (e.g. caching); too much leads to **anomalies**: inconsistent or hard-to-maintain data.

---

## What goes wrong with redundant data

### Update anomalies

If the same fact is stored in many rows, updating it in one place leaves others outdated.

**Example — single table with repeated customer data:**

| order_id | order_date  | customer_name | customer_email    | product_name | quantity |
| -------: | ----------- | ------------- | ----------------- | ------------ | -------- |
| 1        | 2024-01-15  | Emma Virtanen | emma@example.com  | Tent         | 1        |
| 2        | 2024-02-20  | Emma Virtanen | emma@example.com  | Jacket       | 1        |
| 3        | 2024-01-22  | Jussi Mäkinen| jussi@example.com | Sleeping Bag| 1        |

If Emma changes her email, we must update **every** row where she appears. Miss one row → data is inconsistent (two different emails for the same customer).

---

### Insert anomalies

We cannot record a fact until another fact exists, or we are forced to repeat or invent data.

**Example:** We want to add a new customer who has not placed an order yet. With the table above, we have nowhere to put "Liisa Korhonen, liisa@example.com" without inventing a fake order or leaving order columns NULL. The schema does not support "customer without order."

---

### Delete anomalies

Deleting one fact accidentally removes another.

**Example:** If we delete the only order for Jussi Mäkinen, we also lose the only record that Jussi exists as a customer. We might want to keep customer data for history or future orders.

---

## Summary: why we avoid redundancy

| Problem           | Effect                                                                 |
| ----------------- | ---------------------------------------------------------------------- |
| **Update anomaly**| Same fact in many places → easy to update some but not all → inconsistency |
| **Insert anomaly**| Cannot add a valid fact (e.g. customer) without another (e.g. order)     |
| **Delete anomaly**| Deleting one thing (e.g. last order) removes another (e.g. customer)   |

**Normalization** is the process of restructuring tables to remove redundancy and these anomalies, usually by splitting data into more tables and linking them with keys.

---

# 2) Normal Forms (1NF, 2NF, 3NF)

Normal forms are levels of structure. Each level builds on the previous one: a table in 3NF is also in 2NF and 1NF.

---

## First Normal Form (1NF)

A table is in **1NF** if:

1. **Atomic values** — Each cell contains a single value, not a list or nested structure.
2. **Unique rows** — Each row is uniquely identified (e.g. by a primary key).
3. **Consistent columns** — Each column has one meaning and one data type for all rows.

### What 1NF forbids

- **Repeating groups** — e.g. `phone1`, `phone2`, `phone3` or a column holding `"A, B, C"`.
- **No primary key** — so rows are not clearly distinguishable.

### Example — not in 1NF

| student_id | full_name   | courses        |
| ---------: | ----------- | -------------- |
| 1          | Aino Laine  | DB, Algorithms |
| 2          | Mika Virtanen | DB          |

`courses` is not atomic: it holds multiple values in one cell. We cannot reliably query "who takes Algorithms?" or change one course without parsing a string.

### Example — in 1NF

Split into two tables: one row per student, one row per enrollment.

**students**

| student_id | full_name    |
| ---------: | ------------ |
| 1          | Aino Laine   |
| 2          | Mika Virtanen|

**enrollments** (one row per student–course pair)

| student_id | course_id |
| ---------: | --------: |
| 1          | 1         |
| 1          | 2         |
| 2          | 1         |

Each cell is atomic; each row is identifiable (e.g. by `(student_id, course_id)`).

---

## Second Normal Form (2NF)

A table is in **2NF** if it is in 1NF and:

- **No partial dependency** — Every non-key attribute depends on the **whole** primary key, not just part of it.

This matters when the primary key is **composite** (more than one column). If an attribute depends only on part of the key, it is repeated for every combination involving that part → redundancy.

### Example — violates 2NF

| student_id | course_id | full_name   | course_title | grade |
| ---------: | --------: | ----------- | ------------ | ----- |
| 1          | 1         | Aino Laine  | Databases    | 5     |
| 1          | 2         | Aino Laine  | Algorithms   | 4     |
| 2          | 1         | Mika Virtanen | Databases  | 3     |

- Primary key: `(student_id, course_id)`.
- `full_name` depends only on `student_id` → repeated for every course Aino takes (partial dependency).
- `course_title` depends only on `course_id` → repeated for every student in that course (partial dependency).
- `grade` depends on **both** → OK.

So we have redundancy and update/insert/delete anomalies for names and titles.

### Fix: split by dependency

- **students** — `student_id` (PK), `full_name`.
- **courses** — `course_id` (PK), `course_title`.
- **grades** — `(student_id, course_id)` (PK), `grade`.

Now every non-key attribute depends on the full primary key of its table. No partial dependencies → 2NF.

---

## Third Normal Form (3NF)

A table is in **3NF** if it is in 2NF and:

- **No transitive dependency** — No non-key attribute depends on another non-key attribute.

So every non-key attribute must depend **only** on the primary key (or candidate key), not on other non-key columns.

### Example — violates 3NF

| course_id | title      | teacher_id | teacher_name  |
| --------- | ---------- | ---------: | ------------- |
| 1         | Databases  | 1          | Liisa Korhonen|
| 2         | Algorithms | 2          | Pekka Salo    |

- Primary key: `course_id`.
- `teacher_name` depends on `teacher_id`, and `teacher_id` depends on `course_id`. So `teacher_name` depends on `course_id` **via** `teacher_id` (transitive dependency).
- If Liisa changes her name, we must update every course row where she is the teacher → redundancy and update anomaly.

### Fix: remove transitive dependency

- **courses** — `course_id` (PK), `title`, `teacher_id` (FK).
- **teachers** — `teacher_id` (PK), `teacher_name`.

Now `teacher_name` lives only in `teachers`; `courses` just holds the key. No transitive dependency → 3NF.

---

## Quick reference: 1NF, 2NF, 3NF

| Form | Requirement |
| ---- | ------------ |
| **1NF** | Atomic values; unique rows (primary key); one meaning per column. |
| **2NF** | 1NF + no partial dependency (every non-key attribute depends on the **whole** key). |
| **3NF** | 2NF + no transitive dependency (no non-key attribute depends on another non-key attribute). |

In practice: split tables so that each table describes one "thing" (one entity or one relationship), and non-key attributes depend only on that table’s key. Foreign keys link the tables.

---

# 3) When Denormalization Is Acceptable

**Denormalization** means intentionally introducing redundancy (e.g. storing a copy of a value from another table, or combining tables) to simplify queries or improve performance.

Normalization is the default for transactional data: it reduces anomalies and keeps the schema clear. Denormalization is a **trade-off**: you accept some redundancy and extra maintenance in exchange for benefits elsewhere.

---

## Situations where denormalization is often considered

### 1. Read-heavy reporting or analytics

- **Idea:** A reporting table or view might duplicate data from several normalized tables (e.g. pre-joined "order summary" with customer name, product name, totals).
- **Benefit:** Reports run with fewer JOINs and less load on the main transactional schema.
- **Cost:** The duplicated data must be kept in sync (via triggers, ETL, or application logic). Stale or inconsistent data is a risk.

### 2. Performance-critical read paths

- **Idea:** Storing a frequently needed value in the same row where it is read (e.g. `order_total` on `orders` even if it could be computed from `order_items`).
- **Benefit:** Fewer joins or aggregations at read time; sometimes better use of indexes.
- **Cost:** Writes must update the duplicated value; logic is in two places (compute vs. store).

### 3. Simplicity for a specific use case

- **Idea:** A small, fixed-format table (e.g. config or lookup) might repeat a label or code in several columns if it makes one application simpler.
- **Benefit:** Simpler code and queries for that use case.
- **Cost:** Only acceptable when the data is small, rarely changes, and the redundancy is limited and controlled.

### 4. Caches and materialized views

- **Idea:** A materialized view or cache table that stores the result of a complex query (e.g. dashboard summary).
- **Benefit:** Very fast reads; the main schema stays normalized.
- **Cost:** Refresh strategy (when and how to update); may be stale until refresh.

---

## Guidelines

| Do | Avoid |
| ---| ----- |
| Document *why* and *where* you denormalize | Denormalizing the main transactional schema "everywhere" |
| Keep the single source of truth and sync from it | Letting multiple sources drift out of sync |
| Prefer materialized views / reporting tables over changing core tables | Adding redundant columns to core tables without a clear performance need |
| Revisit when requirements or usage change | Denormalizing "just in case" before measuring a real problem |

---

## Summary

| Topic | Key ideas |
| ----- | --------- |
| **Redundancy** | Duplicated facts → update, insert, and delete anomalies. Normalization reduces redundancy by splitting tables and using keys. |
| **1NF** | Atomic values, unique rows, one meaning per column. No repeating groups. |
| **2NF** | No partial dependency: every non-key attribute depends on the full primary key. |
| **3NF** | No transitive dependency: no non-key attribute depends on another non-key attribute. |
| **Denormalization** | Intentional redundancy for performance or simplicity. Use sparingly, document it, and keep a clear source of truth. |

---

_End of Materials 08._
