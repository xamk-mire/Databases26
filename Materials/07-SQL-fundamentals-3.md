# SQL Fundamentals, Part III (PostgreSQL)

### JOINs, Referential Integrity, and Constraints in Detail

In [Materials 05](05-SQL-fundamentals.md) we built tables and introduced `REFERENCES` as a way to link them.  
In [Materials 06](06-SQL-fundamentals-2.md) we learned to filter, sort, aggregate, and briefly touched `JOIN`.

Now we go deeper:

- **JOIN** → How to combine rows from multiple tables in one query
- **Referential integrity** → What foreign keys really enforce, and what happens when referenced rows change
- **Constraints** → All constraint types, how they work, and when to use them

This chapter assumes you know the schema: `students`, `courses`, `enrollments`, `grades`, `teachers`.

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

# 1) JOINs — Combining Tables in One Query

A **JOIN** combines rows from two or more tables based on a relationship between them.  
Without JOINs, you would need multiple separate queries and manual piecing together.

### Why JOINs matter

- Data is split across tables to avoid duplication (normalization).
- Most questions require data from several tables: "Which courses did Aino take?" needs `students` + `enrollments` + `courses`.
- JOINs let you answer these questions in a single query.

---

## JOIN basics: the matching logic

Every JOIN has:

1. **Left table** (the one after `FROM`)
2. **Right table** (the one after `JOIN`)
3. **Join condition** (usually `ON left.column = right.column`)

The condition decides which rows from the left and right tables are paired.

[Good example materials in w3school](https://www.w3schools.com/sql/sql_join.asp)

---

## INNER JOIN — Only matching rows

**INNER JOIN** returns only rows where the join condition is true in both tables.

### Example: Students with their enrolled courses (names and titles)

```sql
SELECT s.full_name, c.title
FROM enrollments e
INNER JOIN students s ON s.student_id = e.student_id
INNER JOIN courses  c ON c.course_id  = e.course_id
ORDER BY s.full_name, c.title;
```

**Result**

| full_name     | title           |
| ------------- | --------------- |
| Aino Laine    | Algorithms      |
| Aino Laine    | Databases       |
| Mika Virtanen | Databases       |
| Olli Koski    | Web Development |
| Sara Niemi    | Databases       |
| Sara Niemi    | Web Development |

**Explanation**

- `enrollments` links students to courses via `student_id` and `course_id`.
- First JOIN: add student names from `students`.
- Second JOIN: add course titles from `courses`.
- Only enrollments that have both a valid student and a valid course appear.

---

### Step-by-step: How the query executes

#### Step 0: Start with the FROM table (`enrollments`)

| student_id | course_id |
| ---------: | --------: |
|          1 |         1 |
|          1 |         2 |
|          2 |         1 |
|          3 |         1 |
|          3 |         3 |
|          4 |         3 |

We begin with 6 rows. Each row is an enrollment event (student X in course Y).

---

#### Step 1: INNER JOIN `students` (match on `student_id`)

For each enrollment row, we look up the student. Match condition: `s.student_id = e.student_id`.

| e.student_id | e.course_id | s.full_name   |
| ------------ | ----------- | ------------- |
| 1            | 1           | Aino Laine    |
| 1            | 2           | Aino Laine    |
| 2            | 1           | Mika Virtanen |
| 3            | 1           | Sara Niemi    |
| 3            | 3           | Sara Niemi    |
| 4            | 3           | Olli Koski    |

Every enrollment has a valid student, so all 6 rows survive. Student names are now attached.

---

#### Step 2: INNER JOIN `courses` (match on `course_id`)

For each row from Step 1, we look up the course. Match condition: `c.course_id = e.course_id`.

| s.full_name   | c.title         |
| ------------- | --------------- |
| Aino Laine    | Databases       |
| Aino Laine    | Algorithms      |
| Mika Virtanen | Databases       |
| Sara Niemi    | Databases       |
| Sara Niemi    | Web Development |
| Olli Koski    | Web Development |

Every enrollment has a valid course, so all 6 rows survive. Course titles are now attached.

---

#### Step 3: SELECT and ORDER BY (final output)

We keep only `full_name` and `title`, then sort by name, then title.

| full_name     | title           |
| ------------- | --------------- |
| Aino Laine    | Algorithms      |
| Aino Laine    | Databases       |
| Mika Virtanen | Databases       |
| Olli Koski    | Web Development |
| Sara Niemi    | Databases       |
| Sara Niemi    | Web Development |

---

### Example: Courses with their teacher names

```sql
SELECT c.title, c.credits, t.full_name AS teacher_name
FROM courses c
INNER JOIN teachers t ON t.teacher_id = c.teacher_id
ORDER BY c.title;
```

**Result**

| title           | credits | teacher_name   |
| --------------- | ------: | -------------- |
| Algorithms      |       6 | Pekka Salo     |
| Databases       |       5 | Liisa Korhonen |
| Web Development |       5 | Maria Lind     |

**Explanation**

- Each course has a `teacher_id` pointing to `teachers`.
- The JOIN brings in the teacher’s name from `teachers` for each course.

---

### Step-by-step: How the query executes

#### Step 0: Start with the FROM table (`courses`)

| course_id | title           | credits | teacher_id |
| --------- | --------------- | ------: | ---------: |
| 1         | Databases       |       5 |          1 |
| 2         | Algorithms      |       6 |          2 |
| 3         | Web Development |       5 |          3 |

---

#### Step 1: INNER JOIN `teachers` (match on `teacher_id`)

For each course row, we look up the teacher. Match condition: `t.teacher_id = c.teacher_id`.

| c.title         | c.credits | t.full_name    |
| --------------- | --------: | -------------- |
| Databases       |         5 | Liisa Korhonen |
| Algorithms      |         6 | Pekka Salo     |
| Web Development |         5 | Maria Lind     |

Each course has exactly one matching teacher. All 3 rows survive.

---

#### Step 2: SELECT and ORDER BY (final output)

| title           | credits | teacher_name   |
| --------------- | ------: | -------------- |
| Algorithms      |       6 | Pekka Salo     |
| Databases       |       5 | Liisa Korhonen |
| Web Development |       5 | Maria Lind     |

---

## LEFT JOIN (LEFT OUTER JOIN) — Keep all rows from the left table

**LEFT JOIN** returns all rows from the left table, and matching rows from the right table.  
If there is no match, the right table’s columns are filled with `NULL`.

### Example: All students and their course count (including those with zero enrollments)

```sql
SELECT s.full_name, COUNT(e.course_id) AS course_count
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.student_id
GROUP BY s.student_id, s.full_name
ORDER BY s.full_name;
```

**Result**

| full_name     | course_count |
| ------------- | -----------: |
| Aino Laine    |            2 |
| Mika Virtanen |            1 |
| Olli Koski    |            1 |
| Sara Niemi    |            2 |

_(With our data, every student has at least one enrollment. If we added a 5th student with no enrollments, they would appear with `course_count = 0`.)_

**Explanation**

- `LEFT JOIN` keeps every row from `students`.
- `COUNT(e.course_id)` counts only non-NULL enrollments; students with no enrollments get 0.

---

### Step-by-step: How the query executes

#### Step 0: Start with the FROM table (`students`)

| student_id | full_name     |
| ---------: | ------------- |
|          1 | Aino Laine    |
|          2 | Mika Virtanen |
|          3 | Sara Niemi    |
|          4 | Olli Koski    |

---

#### Step 1: LEFT JOIN `enrollments` (match on `student_id`)

For each student, we find matching enrollments. **LEFT JOIN keeps every student** even if there are no matches.

| s.student_id | s.full_name   | e.student_id | e.course_id |
| ------------ | ------------- | ------------ | ----------- |
| 1            | Aino Laine    | 1            | 1           |
| 1            | Aino Laine    | 1            | 2           |
| 2            | Mika Virtanen | 2            | 1           |
| 3            | Sara Niemi    | 3            | 1           |
| 3            | Sara Niemi    | 3            | 3           |
| 4            | Olli Koski    | 4            | 3           |

Aino gets 2 rows (2 enrollments), Mika 1, Sara 2, Olli 1. If a student had no enrollments, they would appear once with `e.student_id` and `e.course_id` = NULL.

---

#### Step 2: GROUP BY and COUNT

We group by student and count `e.course_id` (NULLs are not counted).

| full_name     | course_count |
| ------------- | -----------: |
| Aino Laine    |            2 |
| Mika Virtanen |            1 |
| Olli Koski    |            1 |
| Sara Niemi    |            2 |

---

### Example: All courses, with enrollment count (including courses with no enrollments)

Assume we add a course with no enrollments:

```sql
INSERT INTO courses (title, credits, teacher_id) VALUES ('Statistics', 4, 1);
```

```sql
SELECT c.title, COUNT(e.student_id) AS enrollment_count
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.course_id
GROUP BY c.course_id, c.title
ORDER BY c.title;
```

**Result**

| title           | enrollment_count |
| --------------- | ---------------: |
| Algorithms      |                1 |
| Databases       |                3 |
| Statistics      |                0 |
| Web Development |                2 |

**Explanation**

- `LEFT JOIN` keeps every course.
- Statistics has no enrollments → `e.student_id` is NULL for those rows → `COUNT(e.student_id)` = 0.

---

### Step-by-step: How the query executes

#### Step 0: Start with the FROM table (`courses`)

With Statistics added (course_id 4):

| course_id | title           |
| --------- | --------------- |
| 1         | Databases       |
| 2         | Algorithms      |
| 3         | Web Development |
| 4         | Statistics      |

---

#### Step 1: LEFT JOIN `enrollments` (match on `course_id`)

For each course, we find matching enrollments. **LEFT JOIN keeps every course** even if there are no matches.

| c.course_id | c.title         | e.student_id | e.course_id |
| ----------- | --------------- | ------------ | ----------- |
| 1           | Databases       | 1            | 1           |
| 1           | Databases       | 2            | 1           |
| 1           | Databases       | 3            | 1           |
| 2           | Algorithms      | 1            | 2           |
| 3           | Web Development | 3            | 3           |
| 3           | Web Development | 4            | 3           |
| 4           | Statistics      | _(NULL)_     | _(NULL)_    |

Statistics (4) has no enrollments → it appears once with NULL in the enrollment columns. Databases appears 3 times (3 enrollments), Algorithms 1, Web Development 2.

---

#### Step 2: GROUP BY and COUNT

We group by course and count `e.student_id` (NULLs are not counted).

| title           | enrollment_count |
| --------------- | ---------------: |
| Algorithms      |                1 |
| Databases       |                3 |
| Statistics      |                0 |
| Web Development |                2 |

Statistics correctly shows 0.

---

### Example: All courses with teacher names (including courses without an assigned teacher)

If `teacher_id` in `courses` is nullable, some courses might not have a teacher yet.  
`LEFT JOIN teachers` keeps those courses and shows NULL for the teacher name:

```sql
SELECT c.title, t.full_name AS teacher_name
FROM courses c
LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
ORDER BY c.title;
```

With our schema (all courses have teachers), every row gets a teacher name.  
If we had a course with `teacher_id = NULL`, it would still appear, with `teacher_name` as NULL.

---

### Step-by-step: How the query executes

#### Step 0: Start with the FROM table (`courses`)

| course_id | title           | teacher_id |
| --------- | --------------- | ---------: |
| 1         | Databases       |          1 |
| 2         | Algorithms      |          2 |
| 3         | Web Development |          3 |

---

#### Step 1: LEFT JOIN `teachers` (match on `teacher_id`)

For each course, we look up the teacher. **LEFT JOIN keeps every course** even if there is no match.

| c.title         | t.full_name    |
| --------------- | -------------- |
| Databases       | Liisa Korhonen |
| Algorithms      | Pekka Salo     |
| Web Development | Maria Lind     |

With our data, every course has a teacher, so all matches succeed.  
**If** we had a course with `teacher_id = NULL`, it would appear as one row with `teacher_name` = NULL.

---

### Visual: LEFT JOIN keeps all left rows

```
courses (left)       enrollments (right)
─────────────        ──────────────────
Databases (1)   ───► (1,1), (2,1), (3,1)  ✓ matches
Algorithms (2)  ───► (1,2)                ✓ matches
Web Dev (3)     ───► (3,3), (4,3)         ✓ matches
Statistics (4)  ───► (no match)           ✓ still in result, right cols = NULL
```

---

## RIGHT JOIN and FULL OUTER JOIN

### RIGHT JOIN (RIGHT OUTER JOIN)

Same idea as LEFT JOIN, but all rows from the **right** table are kept.  
Rarely needed: you can always rewrite a RIGHT JOIN as a LEFT JOIN by swapping the tables.

### FULL OUTER JOIN

Keeps all rows from both tables.  
Where there is no match, the other side’s columns are NULL.

```sql
SELECT s.full_name, c.title
FROM students s
FULL OUTER JOIN enrollments e ON e.student_id = s.student_id
FULL OUTER JOIN courses c ON c.course_id = e.course_id;
```

Useful when you want "everything from both sides" (e.g. debugging or full reconciliation).

---

## Self-join — Joining a table to itself

A **self-join** joins a table to itself. You use different aliases for the "left" and "right" copies.

### Example: Employees and their managers

Assume an `employees` table:

| employee_id | full_name    | manager_id |
| ----------: | ------------ | ---------: |
|           1 | Anna Boss    |       NULL |
|           2 | Bob Worker   |          1 |
|           3 | Carol Worker |          1 |

```sql
SELECT e.full_name AS employee, m.full_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

**Result**

| employee     | manager   |
| ------------ | --------- |
| Anna Boss    | _(NULL)_  |
| Bob Worker   | Anna Boss |
| Carol Worker | Anna Boss |

---

### Step-by-step: How the self-join executes

#### Step 0: Start with the FROM table (`employees` as `e`)

| e.employee_id | e.full_name  | e.manager_id |
| ------------- | ------------ | -----------: |
| 1             | Anna Boss    |         NULL |
| 2             | Bob Worker   |            1 |
| 3             | Carol Worker |            1 |

---

#### Step 1: LEFT JOIN `employees` as `m` (match `e.manager_id` = `m.employee_id`)

For each employee, we look up their manager in the _same table_ using a different alias (`m`).

| e.full_name  | m.full_name |
| ------------ | ----------- |
| Anna Boss    | _(NULL)_    |
| Bob Worker   | Anna Boss   |
| Carol Worker | Anna Boss   |

- Anna has `manager_id = NULL` → no match → `m.full_name` is NULL.
- Bob and Carol have `manager_id = 1` → match employee 1 (Anna) → `m.full_name` = Anna Boss.

---

## Join conditions: ON vs WHERE

### ON — Part of the join

`ON` specifies which rows are matched between the two tables.

```sql
SELECT s.full_name, c.title
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c ON c.course_id = e.course_id
WHERE c.credits >= 5;
```

- `ON` defines the relationship.
- `WHERE` filters the result after the join.

### USING — When column names match

If both tables use the same column name for the join, you can use `USING`:

```sql
SELECT s.full_name, c.title
FROM enrollments e
JOIN students s USING (student_id)
JOIN courses c USING (course_id);
```

`USING (student_id)` is equivalent to `ON e.student_id = s.student_id` when both tables have `student_id`.

---

## Summary: JOIN types

| JOIN type       | Keeps                                       |
| --------------- | ------------------------------------------- |
| INNER JOIN      | Only rows that match in both tables         |
| LEFT JOIN       | All left rows + matching right rows (NULLs) |
| RIGHT JOIN      | All right rows + matching left rows (NULLs) |
| FULL OUTER JOIN | All rows from both tables                   |

---

# 2) Referential Integrity — What Foreign Keys Enforce

**Referential integrity** means: every foreign key value must point to an existing row in the referenced table (or be NULL if the column allows it).

PostgreSQL enforces this automatically when you define `REFERENCES`.

---

## What the database checks

### On INSERT or UPDATE (in the table with the foreign key)

- You cannot insert `(student_id = 99, course_id = 1)` in `enrollments` if there is no student with `student_id = 99`.
- Same for `course_id`: it must exist in `courses`.

### On DELETE or UPDATE (in the referenced table)

- If you try to delete student 1, PostgreSQL must decide: what happens to enrollments that reference student 1?
- The same question applies when you update a primary key (which is rare and usually discouraged).

You control this with `ON DELETE` and `ON UPDATE`.

---

## ON DELETE and ON UPDATE options

When defining a foreign key, you can specify:

```sql
REFERENCES parent_table(parent_column)
  ON DELETE action
  ON UPDATE action
```

### Common actions

| Action        | Meaning                                                                    |
| ------------- | -------------------------------------------------------------------------- |
| `RESTRICT`    | Block the DELETE/UPDATE if any child rows reference this row (default)     |
| `CASCADE`     | Delete/update child rows when the parent is deleted/updated                |
| `SET NULL`    | Set the foreign key column to NULL in child rows (column must be nullable) |
| `SET DEFAULT` | Set the foreign key to its default value in child rows                     |
| `NO ACTION`   | Same as RESTRICT for deferrable constraints; otherwise similar             |

---

### Example: RESTRICT (default)

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
  course_id  INTEGER NOT NULL REFERENCES courses(course_id)   ON DELETE RESTRICT,
  PRIMARY KEY (student_id, course_id)
);
```

If you try:

```sql
DELETE FROM students WHERE student_id = 1;
```

PostgreSQL returns an error, because enrollments reference student 1.

---

### Example: CASCADE

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
  course_id  INTEGER NOT NULL REFERENCES courses(course_id)   ON DELETE CASCADE,
  PRIMARY KEY (student_id, course_id)
);
```

If you delete student 1:

```sql
DELETE FROM students WHERE student_id = 1;
```

PostgreSQL also deletes all `enrollments` rows where `student_id = 1`.

**Use CASCADE with care** — it can remove a lot of data.

---

### Example: SET NULL

Requires the foreign key column to be nullable:

```sql
CREATE TABLE grades (
  student_id INTEGER REFERENCES students(student_id) ON DELETE SET NULL,
  course_id  INTEGER REFERENCES courses(course_id)   ON DELETE SET NULL,
  grade      INTEGER,
  PRIMARY KEY (student_id, course_id)
);
```

When you delete a student, `student_id` in their grade rows becomes NULL.  
_Note: This changes the meaning of the table; usually RESTRICT or CASCADE is preferred for enrollments/grades._

---

### Example: Teachers and courses — SET NULL when teacher is removed

If a course can exist without a teacher, use `ON DELETE SET NULL`:

```sql
CREATE TABLE courses (
  course_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title      VARCHAR(200) NOT NULL,
  credits    INTEGER NOT NULL,
  teacher_id INTEGER REFERENCES teachers(teacher_id) ON DELETE SET NULL
);
```

When you delete a teacher, their courses remain, but `teacher_id` becomes NULL (course is "unassigned").

---

## When to use which option

| Scenario                                         | Typical choice                     |
| ------------------------------------------------ | ---------------------------------- |
| Child rows only make sense with parent           | `ON DELETE CASCADE`                |
| Child rows must never reference a missing parent | `ON DELETE RESTRICT`               |
| Want to "unlink" but keep child rows             | `ON DELETE SET NULL` (if nullable) |

---

# 3) Constraints in Detail

Constraints are rules the database enforces.  
They keep data consistent and meaningful.

---

## Constraint types in PostgreSQL

| Constraint  | Purpose                                                  |
| ----------- | -------------------------------------------------------- |
| PRIMARY KEY | Uniquely identifies each row; implies NOT NULL           |
| FOREIGN KEY | References another table; enforces referential integrity |
| UNIQUE      | No two rows may have the same value(s) in the column(s)  |
| NOT NULL    | Column cannot contain NULL                               |
| CHECK       | Value must satisfy a boolean expression                  |
| DEFAULT     | Value to use when none is provided on INSERT             |

---

## PRIMARY KEY

- Each row has a unique identifier.
- Only one PRIMARY KEY per table (but it can be composite: multiple columns).
- Implies `NOT NULL` and `UNIQUE`.

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL
);
```

Composite primary key:

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  PRIMARY KEY (student_id, course_id)
);
```

---

## FOREIGN KEY (REFERENCES)

- Links a column (or columns) to a primary key or unique column in another table.
- Ensures every non-NULL value exists in the referenced table.

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  PRIMARY KEY (student_id, course_id)
);
```

Named constraint (useful for error messages and management):

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL,
  course_id  INTEGER NOT NULL,
  PRIMARY KEY (student_id, course_id),
  CONSTRAINT fk_enrollments_student
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  CONSTRAINT fk_enrollments_course
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE RESTRICT
);
```

---

## UNIQUE

- No two rows may have the same value (or combination of values) in the constrained column(s).
- NULL is allowed (multiple NULLs are often allowed in PostgreSQL for UNIQUE columns).

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email      VARCHAR(255) UNIQUE
);
```

---

## NOT NULL

- Column cannot be NULL.
- Often used for required attributes: name, id, date, etc.

```sql
CREATE TABLE teachers (
  teacher_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);

CREATE TABLE courses (
  course_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title      VARCHAR(200) NOT NULL,
  credits    INTEGER NOT NULL,
  teacher_id INTEGER REFERENCES teachers(teacher_id)
);
```

---

## CHECK

- Value must satisfy a boolean expression.
- Enforces business rules directly in the database.

```sql
CREATE TABLE courses (
  course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title     VARCHAR(200) NOT NULL,
  credits   INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 20)
);
```

```sql
CREATE TABLE grades (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  grade      INTEGER CHECK (grade >= 0 AND grade <= 5),
  PRIMARY KEY (student_id, course_id)
);
```

Named CHECK constraint:

```sql
CREATE TABLE grades (
  ...
  CONSTRAINT chk_grade_range CHECK (grade >= 0 AND grade <= 5)
);
```

---

## DEFAULT

- Provides a value when INSERT omits the column.

```sql
CREATE TABLE fines (
  fine_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  amount    NUMERIC(6,2) NOT NULL,
  paid      BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Adding and altering constraints

### Add constraint to existing table

```sql
ALTER TABLE students
  ADD CONSTRAINT uq_students_email UNIQUE (email);
```

```sql
ALTER TABLE grades
  ADD CONSTRAINT chk_grade_range CHECK (grade >= 0 AND grade <= 5);
```

### Drop constraint

```sql
ALTER TABLE students DROP CONSTRAINT uq_students_email;
```

### Make column NOT NULL

```sql
ALTER TABLE students ALTER COLUMN full_name SET NOT NULL;
```

---

## Naming constraints (good practice)

Named constraints make errors easier to understand and schema changes easier to manage:

| Convention  | Example                    |
| ----------- | -------------------------- |
| Primary key | `pk_table` or `table_pkey` |
| Foreign key | `fk_child_parent`          |
| Unique      | `uq_table_column`          |
| Check       | `chk_table_description`    |

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL,
  course_id  INTEGER NOT NULL,
  CONSTRAINT pk_enrollments PRIMARY KEY (student_id, course_id),
  CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students(student_id),
  CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

---

## Summary

| Topic                     | Key ideas                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **INNER JOIN**            | Only matching rows from both tables                                                  |
| **LEFT JOIN**             | All left rows + matches from right (NULLs where no match)                            |
| **Referential integrity** | Foreign keys must reference existing rows; use ON DELETE/UPDATE to control behaviour |
| **Constraints**           | PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, DEFAULT                           |
| **Naming**                | Name constraints for clearer errors and easier maintenance                           |

---

_End of Materials 07._
