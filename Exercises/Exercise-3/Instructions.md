# **Exercise 3: SQL Fundamentals — Library Checkout System (PostgreSQL)**

# **Build a library checkout database and practice queries**

> **Instructions:**
> Work through each section in order. Build a small library checkout database from scratch: create a new database, define the tables (Books, Authors, BookAuthors, Members, Loans, Fines), insert the example data, then practice queries. Write your SQL in the code blocks provided. Refer to Materials 05 (SQL fundamentals) and 06 (SQL fundamentals, part 2) as needed.

---

## **PART A — Building the database**

Based on [Materials/05-SQL-fundamentals.md](../../Materials/05-SQL-fundamentals.md). You will create the database, write all `CREATE TABLE` statements, insert the example data, and run basic `SELECT` queries to verify.

---

### **A0 — Create a new database**

Create a new PostgreSQL database named **`library_db`**.

You can run this in **psql** (connect to PostgreSQL first, then run the command) or create the database via **pgAdmin** (right-click Databases → Create → Database, name it `library_db`). Then connect to `library_db` for all following steps.

**Write your SQL (if using psql):**

```sql
create database library_db;


```

---

### **A1 — CREATE TABLE (six tables)**

Create the following tables in **dependency order** (referenced tables first). Use the column specifications below. Use **snake_case** for table and column names. Every table should have a primary key; use `GENERATED ALWAYS AS IDENTITY` for integer surrogate keys where indicated.

**Table specifications:**

| Table | Columns and constraints |
| ----- | ----------------------- |
| **books** | `book_id` INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, `title` VARCHAR(300) NOT NULL, `isbn` VARCHAR(20) UNIQUE (nullable), `publication_year` INTEGER CHECK (publication_year BETWEEN 1000 AND 2100) |
| **authors** | `author_id` INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, `full_name` VARCHAR(100) NOT NULL |
| **book_authors** | `book_id` INTEGER NOT NULL REFERENCES books(book_id), `author_id` INTEGER NOT NULL REFERENCES authors(author_id), PRIMARY KEY (book_id, author_id) |
| **members** | `member_id` INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, `full_name` VARCHAR(100) NOT NULL, `email` VARCHAR(255) UNIQUE (nullable) |
| **loans** | `loan_id` INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, `book_id` INTEGER NOT NULL REFERENCES books(book_id), `member_id` INTEGER NOT NULL REFERENCES members(member_id), `loan_date` DATE NOT NULL, `due_date` DATE NOT NULL, `return_date` DATE (nullable) |
| **fines** | `fine_id` INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, `loan_id` INTEGER NOT NULL REFERENCES loans(loan_id), `amount` NUMERIC(6,2) NOT NULL CHECK (amount >= 0), `paid` BOOLEAN NOT NULL DEFAULT FALSE |

**Creation order:** books → authors → book_authors → members → loans → fines.

**Write your CREATE TABLE statements here:**

```sql
-- books

create table books (
    book_id int generated always as identity primary key,
    title varchar(300) not null,
    isbn varchar(20) unique null,
    publication_year int check (publication_year between 1000 and 2100)
);

-- authors

create table authors (
    author_id int generated always as identity primary key,
    full_name varchar(100) not null
);

-- book_authors
create table book_authors (
    book_id int not null references books(book_id),
    author_id int not null references authors(author_id),
    primary key (book_id, author_id)
);

-- members

create table members (
    member_id int generated always as identity primary key,
    full_name varchar(100) not null,
    email varchar(255) unique null
);

-- loans

create table loans (
    loan_id int generated always as identity primary key,
    book_id int not null references books(book_id),
    member_id int not null references members(member_id),
    loan_date date not null,
    due_date date not null,
    return_date date null
);
-- fines

create table fines (
    fine_id int generated always as identity primary key,
    loan_id int not null references loans(loan_id),
    amount numeric(6,2) not null check (amount >= 0),
    paid boolean not null default false
);

```

---

### **A2 — INSERT example data**

Insert the rows below into each table. **Omit identity columns** (PostgreSQL will generate them). Insert in this order: books, authors, book_authors, members, loans, fines (so foreign keys exist before you reference them).

**Data to insert:**

**books** (title, isbn, publication_year):

| title            | isbn             | publication_year |
| ---------------- | ---------------- | ---------------- |
| The Great Novel  | 978-0-00-000001-1 | 2020             |
| Databases 101    | 978-0-00-000002-2 | 2019             |
| Web Development  | _(NULL)_         | 2021             |
| Algorithms       | 978-0-00-000004-4 | 2018             |

**authors** (full_name):

| full_name    |
| ------------ |
| Jane Smith   |
| Mika Virtanen |
| Aino Laine   |

**book_authors** (book_id, author_id):

| book_id | author_id |
| ------- | --------- |
| 1       | 1         |
| 1       | 2         |
| 2       | 1         |
| 2       | 2         |
| 3       | 2         |
| 3       | 3         |
| 4       | 3         |

**members** (full_name, email):

| full_name    | email           |
| ------------ | --------------- |
| Aino Laine   | aino@library.fi |
| Mika Virtanen | mika@library.fi |
| Sara Niemi   | _(NULL)_        |
| Olli Koski   | olli@gmail.com  |

**loans** (book_id, member_id, loan_date, due_date, return_date):

| book_id | member_id | loan_date   | due_date    | return_date |
| ------- | --------- | ----------- | ----------- | ----------- |
| 1       | 1         | 2024-01-01  | 2024-01-15  | 2024-01-10  |
| 2       | 1         | 2024-02-01  | 2024-02-15  | _(NULL)_    |
| 1       | 2         | 2024-01-10  | 2024-01-25  | 2024-01-20  |
| 3       | 2         | 2024-03-01  | 2024-03-15  | _(NULL)_    |
| 2       | 3         | 2024-02-10  | 2024-02-24  | 2024-02-20  |
| 4       | 4         | 2024-03-10  | 2024-03-24  | 2024-03-20  |

**fines** (loan_id, amount, paid):

| loan_id | amount | paid  |
| ------- | ------ | ----- |
| 1       | 2.00   | TRUE  |
| 3       | 5.50   | FALSE |
| 5       | 10.00  | TRUE  |
| 6       | 3.00   | FALSE |

**Write your INSERT statements here:**

```sql
-- books

insert into books (title, isbn, publication_year) values
('The Great Novel', '978-0-00-000001-1', 2020),
('Databases 101', '978-0-00-000002-2', 2019),
('Web Development', null, 2021),
('Algorithms', '978-0-00-000004-4', 2018);

-- authors
insert into authors (full_name) values ('Jane Smith'), ('Mika Virtanen'), ('Aino Laine');


-- book_authors
insert into book_authors (book_id, author_id) values (1,1), (1,2), (2,1), (2,2), (3,2), (3,3), (4,3);


-- members

insert into members (full_name, email) values 
('Aino Laine', 'aino@library.fi'),
('Mika Virtanen', 'mika@library.fi'),
('Sara Niemi', null),
('Olli Koski', 'olli@gmail.com');
-- loans

insert into loans (book_id, member_id, loan_date, due_date, return_date) values
(1, 1, '2024-01-01', '2024-01-15', '2024-01-10'),
(2, 1, '2024-02-01', '2024-02-15', null),
(1, 2, '2024-01-10', '2024-01-25', '2024-01-20'),
(3, 2, '2024-03-01', '2024-03-15', null),
(2, 3, '2024-02-10', '2024-02-24', '2024-02-20'),
(4, 4, '2024-03-10', '2024-03-24', '2024-03-20');

-- fines
insert into fines (loan_id, amount, paid) values 
(1, 2.00, true), (3, 5.50, false), (5, 10.00, true), (6, 3.00, false);

```

---

### **A3 — Basic SELECT (verification)**

Run two queries to confirm the data is in place:

1. Select **all columns** from one table (e.g. `books` or `members`).
2. Select **only specific columns** from another table (e.g. `title` and `publication_year` from `books`).

**Write your SELECT statements here:**

```sql
-- 1. All columns from one table
select * from members;

-- 2. Specific columns from another table
select title, publication_year from books;

```

---

## **PART B — Query practice**

Based on [Materials/06-SQL-fundamentals-2.md](../../Materials/06-SQL-fundamentals-2.md). Use the library schema (Books, Authors, BookAuthors, Members, Loans, Fines). For each task, write the SQL in the code block. Use the **Expected / Self-check** hint to verify your result.

---

### **B1 — WHERE (filtering)**

**B1.1** List books with `publication_year` equal to 2020.

*Expected: 1 row (The Great Novel).*

```sql
select * from books where publication_year = 2020; 


```

---

**B1.2** List members whose email is **not** `aino@library.fi`. (Remember: NULL email will not appear in this result.)

*Self-check: 2 rows (Mika Virtanen, Olli Koski).*

```sql
select * from members where email != 'aino@library.fi'; 


```

---

**B1.3** List fines with `amount` greater than 5.

*Self-check: 2 rows (5.50 and 10.00).*

```sql
select * from fines where amount > 5; 


```

---

**B1.4** List loans where `book_id` is 1 **OR** `book_id` is 2.

*Self-check: 4 rows.*

```sql
select * from loans where book_id = 1 or book_id = 2; 


```

---

**B1.5** List members with `member_id` IN (1, 3).

*Self-check: 2 rows (Aino Laine, Sara Niemi).*

```sql
select * from members where member_id in (1, 3); 


```

---

**B1.6** List books with `publication_year` BETWEEN 2018 AND 2020 (inclusive).

*Self-check: 3 rows.*

```sql
select * from books where publication_year between 2018 and 2020; 


```

---

**B1.7** List members whose email ends with `@library.fi`.

*Self-check: 2 rows.*

```sql
select * from members where email like '%@library.fi'; 


```

---

**B1.8** List members who have **no** email (email IS NULL).

*Self-check: 1 row (Sara Niemi).*

```sql
select * from members where email is null; 


```

---

**B1.9** List loans that are **not yet returned** (return_date IS NULL).

*Self-check: 2 rows.*

```sql
select * from loans where return_date is null;


```

---

### **B2 — ORDER BY and LIMIT**

**B2.1** List all books ordered by `publication_year` **descending**, then by `title` **ascending** (for ties).

*Self-check: First row is Web Development (2021), then The Great Novel (2020), then Databases 101 (2019), then Algorithms (2018).*

```sql
select * from books order by publication_year desc, title asc;


```

---

**B2.2** List the **top 2** books by `publication_year` (newest first). Use ORDER BY and LIMIT.

*Self-check: 2 rows (Web Development, The Great Novel).*

```sql
select * from books order by publication_year desc limit 2;


```

---

### **B3 — Aggregation**

**B3.1** How many books are in the database? Use `COUNT(*)` and give the result column an alias (e.g. `book_count`).

*Self-check: 4.*

```sql
select count(*) as book_count from books;


```

---

**B3.2** How many members have an email? Use `COUNT(email)`.

*Self-check: 3 (Sara has NULL email).*

```sql

select count(email) from members;

```

---

**B3.3** What is the **average** fine amount? Use `AVG(amount)` with an alias.

*Self-check: 5.125 (or 5.13 depending on rounding).*

```sql
select avg(amount) as avg_fine_val from fines;


```

---

**B3.4** What is the **total** amount of **unpaid** fines (where paid = FALSE)? Use `SUM(amount)` and WHERE.

*Self-check: 8.50 (5.50 + 3.00).*

```sql
select sum(amount) from fines where paid = false;


```

---

### **B4 — GROUP BY and HAVING**

**B4.1** For each member, show `member_id` and the **number of loans**. Use `GROUP BY member_id` and `COUNT(*)` with an alias (e.g. `loan_count`). Order by `loan_count` descending.

*Self-check: Member 1 & 2 both have 2 loans; members 3 & 4 each have 1.*

```sql
select member_id, count(*) as num_loans from loans group by member_id order by num_loans desc;


```

---

**B4.2** List only members who have **at least 2 loans**. Use the same grouping as B4.1 and add `HAVING COUNT(*) >= 2`.

*Self-check: 2 rows, members 1 & 2*

```sql
select member_id, count(*) as num_loans from loans group by member_id having count(*) >= 2;


```

---

**B4.3** For each author, show `author_id` and the **number of books** they wrote (via `book_authors`). Use `GROUP BY author_id`. Order by book count descending.

*Self-check: Authors 2 has 3 books; author 1 and 3 have 2 books each.*

```sql

select author_id, count(*) as total_books from book_authors group by author_id order by total_books desc;

```

---

### **B5 — Aliases**

**B5.1** Count the total number of loans. Use `COUNT(*) AS total_loans`.

*Self-check: 6.*

```sql
select count(*) as total_loans_in_system from loans;


```

---

**B5.2** List each loan with the **member’s full name** and the **book title**. Use JOINs between `loans`, `members`, and `books`. Use **table aliases** (e.g. `l`, `m`, `b`). Order by member name, then book title.

*Self-check: 6 rows; first row might be Aino Laine with a book title.*

```sql
select m.full_name, b.title 
from loans l
join members m on l.member_id = m.member_id
join books b on l.book_id = b.book_id
order by m.full_name, b.title;


```

---

### **B6 — Combined query (optional)**

**B6.1** List **member full names** that have **at least 2 loans**, with their loan count, ordered by loan count **descending** then by name. Use JOIN(s), GROUP BY, HAVING, and ORDER BY.

*Self-check: 1 row — Aino Laine with loan_count 2.*

```sql
select m.full_name, count(*) as loan_count
from loans l
join members m on l.member_id = m.member_id
group by m.full_name
having count(*) >= 2
order by loan_count desc, m.full_name;


```

---

## **Self-check (validation)**

Confirm the following:

1. Does B1.1 return exactly 1 row? YES
2. Does B1.8 return exactly 1 row (Sara Niemi)? YES
3. Does B3.1 return 4? YES
4. Does B4.2 return exactly 1 row? NO
5. Does B5.1 return 6? YES
6. B6.1 RETURN 2  ROW?  **!!! NOT OK???***

   ---

---

*End of Exercise 3.*
