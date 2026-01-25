# SQL in PostgreSQL

In the previous [materials](04-PostgreSQL.md), PostgreSQL was introduced as a **carefully governed city of information**—
a place where data is not only stored, but **protected**, **structured**, and **kept consistent**.

Now we learn the language used to build that city.

SQL is not only a tool for asking questions.
At the beginning, it is a tool for **creating foundations**:

- shaping tables,
- establishing rules,
- placing the first rows of data,
- and opening the door to the simplest queries.

This lecture focuses on three essential skills:

- **Creating tables** (DDL)
- **Inserting data** (DML)
- **Basic SELECT** (reading what exists)

Nothing more is needed to build your first working database.

---

## 1) What SQL Is in PostgreSQL

SQL (**Structured Query Language**) is the standard language used to communicate with PostgreSQL.

It lets us describe _structure_ and _action_ with clarity:

- **Structure**: “What does the data look like?”
- **Action**: “What should the database store?”
- **Reading**: “Show me what is in the table.”

In PostgreSQL, SQL statements are executed one by one, like carefully written commands.

### Key SQL ideas (keywords)

- **Statement** → one complete instruction ending with `;`
- **Keyword** → command words such as `CREATE`, `INSERT`, `SELECT`
- **Identifier** → names of tables and columns
- **Literal** → actual values, like `'Aino'` or `5`

---

## 2) Creating Tables: Writing the Structure of the World

A database begins empty—like a notebook with no lines.
Tables are the lines. The structure. The promise of order.

To create a table in PostgreSQL, we use:

- **CREATE TABLE**
- column definitions
- constraints that enforce correctness

### The general form of `CREATE TABLE`

```sql
CREATE TABLE table_name (
  column_name data_type constraints,
  ...
);
```

### Key points to remember

- Table and column names are often written in **snake_case**

  - `student_id`, `full_name`, `created_at`

- PostgreSQL treats unquoted names as lowercase by default
- Every table should have a **primary key**
- Columns should use meaningful types and constraints

---

### Example 1: Creating a `students` table (PostgreSQL)

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);
```

#### Explanation (what each part means)

- **student_id**

  - `INTEGER` → whole number
  - `GENERATED ALWAYS AS IDENTITY` → PostgreSQL generates it automatically
  - `PRIMARY KEY` → uniquely identifies each student

- **full_name**

  - text up to 100 characters
  - `NOT NULL` → every student must have a name

- **email**

  - text up to 255 characters
  - `UNIQUE` → no two students may share the same email

✅ This table captures:

- identity (**PRIMARY KEY**)
- required values (**NOT NULL**)
- uniqueness (**UNIQUE**)

---

## 3) Creating Another Table: A Second Concept Enters

A well-designed database grows one concept at a time.

Here we introduce **courses**.

### Example 2: Creating a `courses` table

```sql
CREATE TABLE courses (
  course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title     VARCHAR(200) NOT NULL,
  credits   INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 20)
);
```

#### Explanation

- **course_id** is the identity of the course
- **title** is required text
- **credits** must exist and must be between 1 and 20

The `CHECK` constraint is PostgreSQL’s way of enforcing meaning:

> “Credits are not just numbers—they are _reasonable numbers_.”

---

## 4) Relationships in Table Creation (Optional but Natural)

Even in early courses, students often meet the idea of tables that refer to each other.

The cleanest beginner example is a **junction table** that connects students and courses.

### Example 3: Creating `enrollments` (linking two tables)

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  PRIMARY KEY (student_id, course_id)
);
```

#### What this teaches

- **REFERENCES** creates a foreign key
- PostgreSQL enforces that referenced rows must exist
- composite primary key prevents duplicate enrollments

This table doesn’t describe a student or a course.
It describes a _relationship_:

> “This student is enrolled in this course.”

---

## 5) Inserting Data: Filling the Tables With Life

Tables are structures.
But a database without data is a museum with empty halls.

To add rows, we use **INSERT INTO**.

### The general form of INSERT

```sql
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);
```

### Important insertion rules

- values must match the listed column order
- text values use **single quotes**

  - `'Aino Laine'`

- identity columns (like `student_id`) are usually omitted

  - PostgreSQL generates them

---

### Example 4: Insert students

```sql
INSERT INTO students (full_name, email)
VALUES
  ('Aino Laine', 'aino@uni.fi'),
  ('Mika Virtanen', 'mika@uni.fi');
```

#### Explanation

- We insert two rows at once
- `student_id` is not mentioned → PostgreSQL fills it automatically
- full_name and email are stored as provided

---

### Example 5: Insert courses

```sql
INSERT INTO courses (title, credits)
VALUES
  ('Databases', 5),
  ('Algorithms', 6);
```

Again, course IDs are generated.

---

### Example 6: Insert enrollments

```sql
INSERT INTO enrollments (student_id, course_id)
VALUES
  (1, 1),
  (2, 1);
```

#### Explanation

This assumes:

- student with `student_id = 1` exists
- course with `course_id = 1` exists

If you insert an enrollment with an ID that does not exist, PostgreSQL will reject it, because foreign keys enforce reality:

> “You cannot enroll a student that does not exist.”

---

## 6) Basic SELECT: Reading What Exists

A database is not meant to be written once and forgotten.
You must be able to look inside it.

The simplest way is with **SELECT**.

### The general form of SELECT

```sql
SELECT column1, column2, ...
FROM table_name;
```

At this stage, SELECT is used to:

- confirm data exists
- inspect table contents
- verify the results of inserts

---

### Example 7: View all students

```sql
SELECT * FROM students;
```

#### Explanation

- `*` means “all columns”
- returns every row in the table

This is perfect for early learning and debugging.

---

### Example 8: View specific columns

```sql
SELECT full_name, email
FROM students;
```

#### Explanation

This shows only what is listed:

- student names
- student emails

It teaches an important habit:

> Selecting only what you need makes your intent clearer.

---

### Example 9: View all courses

```sql
SELECT * FROM courses;
```

---

### Example 10: View enrollments

```sql
SELECT * FROM enrollments;
```

Even without more advanced querying, this reveals relationships through IDs.

---

## 7) A Complete “First SQL Session” Script (PostgreSQL)

This script is intentionally simple:

- create structure
- insert data
- read data back

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);

CREATE TABLE courses (
  course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title     VARCHAR(200) NOT NULL,
  credits   INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 20)
);

CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  PRIMARY KEY (student_id, course_id)
);

INSERT INTO students (full_name, email)
VALUES
  ('Aino Laine', 'aino@uni.fi'),
  ('Mika Virtanen', 'mika@uni.fi');

INSERT INTO courses (title, credits)
VALUES
  ('Databases', 5),
  ('Algorithms', 6);

INSERT INTO enrollments (student_id, course_id)
VALUES
  (1, 1),
  (2, 1);

SELECT * FROM students;
SELECT * FROM courses;
SELECT * FROM enrollments;
```
