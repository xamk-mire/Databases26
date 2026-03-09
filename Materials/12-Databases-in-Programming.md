# Databases in Programming: Purpose and Typical Use

## 1) Why Do Programmers Use Databases?

### The core problem: programs need to remember

A running program keeps data in **memory** (variables, objects, arrays). When the program exits or the machine restarts, that data is gone—unless it is stored somewhere persistent.

Databases exist to solve this problem at scale:

- **Persistence** — data survives program restarts, server reboots, and power loss
- **Sharing** — many users, many processes, or many servers can work with the same data
- **Correctness** — the database enforces rules (constraints, transactions) so data stays consistent
- **Efficiency** — indexes and query optimizers make it practical to work with large amounts of data

Without a database, programmers would need to build all of this themselves—and most applications would end up reinventing something fragile.

### What programmers get from a database

| Need                           | What the database provides                                   |
| ------------------------------ | ------------------------------------------------------------ |
| Store data beyond a single run | Persistent storage on disk (or replication)                  |
| Query data flexibly            | SQL (or similar) — ask _what_ you want, not _how_ to find it |
| Keep data consistent           | Constraints, transactions, integrity rules                   |
| Support many users at once     | Concurrency control, isolation                               |
| Recover from failures          | Durability, logging, backup/restore                          |
| Control who can do what        | Users, roles, permissions                                    |
| Handle growth                  | Indexes, partitioning, scaling options                       |

Databases are the **system of record** for most applications: the place where the “real” state of the business or product lives.

---

## 2) Where Databases Fit in Application Architecture

### The typical layers

Most applications separate concerns into layers. The database sits at the bottom, as the **data layer**.

```
┌─────────────────────────────────────┐
│  Presentation (UI, API endpoints)   │
├─────────────────────────────────────┤
│  Business Logic (rules, workflows)  │
├─────────────────────────────────────┤
│  Data Access (queries, mappings)    │
├─────────────────────────────────────┤
│  Database (storage, integrity)      │
└─────────────────────────────────────┘
```

- **Presentation** — receives user input or API requests
- **Business logic** — applies rules (e.g., “can this user place this order?”)
- **Data access** — sends queries to the database and maps results to application objects
- **Database** — stores data, enforces constraints, executes queries

The application code _talks to_ the database; it does not _replace_ it. The database remains responsible for storage, integrity, and efficient query execution.

### Request–response flow (simplified)

A typical flow when a user performs an action:

1. User submits a request (e.g., “Show my orders”).
2. Presentation layer receives it.
3. Business logic decides what data is needed.
4. Data access layer executes a query (e.g., `SELECT * FROM orders WHERE user_id = ?`).
5. Database returns rows.
6. Data access layer maps rows to objects (e.g., `Order`).
7. Business logic may process or filter.
8. Presentation layer formats and returns the response.

The database is involved at steps 4–5: it receives a query and returns data.

---

## 3) How Programs Connect to Databases

### Database drivers and connection strings

To use a database, the application must **connect** to it. This is done via:

- A **database driver** — a library that speaks the database’s protocol (e.g., `pg` for Node.js, `psycopg2` for Python, JDBC for Java)
- A **connection string** — parameters that identify the database and how to reach it

Example connection string (PostgreSQL):

```
postgresql://username:password@hostname:5432/database_name
```

The application uses the driver to open a connection, send SQL, and receive results. Each programming language has its own ecosystem of drivers.

### Connection lifecycle

1. **Open** — establish a connection to the database (often at startup or on first request)
2. **Use** — send queries and receive results
3. **Close** — release the connection when done

Connections are a limited resource. Applications often use **connection pools**—a set of reusable connections—so they don’t open and close a new connection for every single query.

---

## 4) How Programs Talk to the Database

### Option 1: Raw SQL

The most direct way is to send **SQL strings** to the database via the driver.

```python
# Python with psycopg2 (conceptual)
cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
rows = cursor.fetchall()
```

```javascript
// Node.js with pg (conceptual)
const result = await pool.query('SELECT id, name FROM users WHERE email = $1', [
  email,
]);
```

**Important:** Always use **parameterized queries** (placeholders like `%s`, `$1`) instead of string concatenation. This prevents SQL injection and lets the database optimize repeated queries.

### Option 2: Query builders

Query builders are libraries that let you construct SQL programmatically:

```javascript
// Conceptual query builder
db.select('id', 'name').from('users').where('email', '=', email);
```

Benefits: less string manipulation, some protection against mistakes. You still work close to SQL.

### Option 3: ORMs (Object-Relational Mappers)

ORMs map database tables to programming-language **objects** (classes, structs). You work with objects; the ORM generates SQL.

```python
# Conceptual ORM (e.g., SQLAlchemy, Django ORM)
user = User.query.filter_by(email=email).first()
```

```javascript
// Conceptual ORM (e.g., Sequelize, TypeORM)
const user = await User.findOne({ where: { email } });
```

Benefits: familiar object-oriented style, less boilerplate for simple CRUD. Tradeoffs: you may lose control over exact SQL; complex queries can be harder to express or optimize.

| Approach      | Control | Abstraction | Best when                                     |
| ------------- | ------- | ----------- | --------------------------------------------- |
| Raw SQL       | High    | Low         | Complex queries, performance tuning           |
| Query builder | Medium  | Medium      | Readable queries without string concatenation |
| ORM           | Lower   | High        | Standard CRUD, rapid development              |

---

## 5) The Four Operations: CRUD from Code

Most application–database interaction boils down to **CRUD**:

| Operation  | SQL      | Typical use in code                             |
| ---------- | -------- | ----------------------------------------------- |
| **Create** | `INSERT` | Add a new user, order, or record                |
| **Read**   | `SELECT` | Load data to display or process                 |
| **Update** | `UPDATE` | Change existing records (e.g., status, profile) |
| **Delete** | `DELETE` | Remove records when no longer needed            |

Programmers rarely write SQL by hand for every single operation; they use patterns (functions, repository classes, ORM methods) that wrap these operations. Under the hood, the database still receives INSERT, SELECT, UPDATE, or DELETE.

### Example: Create and Read

Conceptually, when a user signs up:

1. Application receives `email`, `name`, `password`.
2. Business logic validates input.
3. Data access executes: `INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)`.
4. Database inserts the row and returns (e.g., the new `id`).
5. Application may return a success message or the new user object.

When a user logs in:

1. Application receives `email`, `password`.
2. Data access executes: `SELECT id, name, password_hash FROM users WHERE email = ?`.
3. Database returns the matching row (or nothing).
4. Application verifies the password and creates a session.

---

## 6) Transactions in Application Code

Some operations must be **all-or-nothing**. For example, transferring money: debit one account, credit another. If the second step fails, the first must be undone.

Databases provide **transactions** for this. From application code, the pattern is:

1. **Begin** a transaction
2. Execute one or more queries
3. **Commit** if everything succeeded, or **Rollback** if something failed

```python
# Conceptual transaction pattern
with connection.transaction():
    cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    # Commit happens automatically on success; rollback on exception
```

Many ORMs and frameworks handle this implicitly (e.g., “one transaction per request”). Understanding transactions is important for correctness when multiple tables or rows must stay in sync.

---

## 7) Common Use Cases in Programming

### Web applications

- **Backend** (Node.js, Python, Java, etc.) connects to a database
- User actions trigger queries (load page data, submit forms)
- Session data may be stored in the database (or in a cache)
- Typical: relational database for users, orders, products; possibly Redis for caching

### Mobile apps

- Mobile app talks to an **API** (REST, GraphQL)
- The API server uses a database to store and retrieve data
- The mobile app never connects directly to the database; it goes through the API for security and centralization

### Microservices

- Each service may have its own database (or schema)
- Services communicate via APIs; databases are not shared directly
- Each service owns its data and uses the database as its source of truth

### Background jobs and workers

- Jobs read from a queue (or a table used as a queue)
- Workers process items and update the database (e.g., “order shipped”, “email sent”)
- The database records the current state of each job

### Reporting and analytics

- Applications (or separate jobs) query the database for reports, dashboards, exports
- Sometimes data is copied to a data warehouse for heavy analytics; the main application database remains the transactional system of record

---

## 8) Security Considerations When Using Databases in Code

### SQL injection

**Never** build SQL by concatenating user input:

```python
# DANGEROUS
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

Use **parameterized queries** instead:

```python
# SAFE
cursor.execute("SELECT * FROM users WHERE email = %s", (user_input,))
```

### Credentials and configuration

- Never hardcode database passwords in source code
- Use environment variables or a secure configuration system
- Restrict database user permissions: the application should not need `SUPERUSER` or schema-altering rights for normal operation

### Least privilege

- Create a dedicated database user for the application
- Grant only the permissions needed (e.g., `SELECT`, `INSERT`, `UPDATE`, `DELETE` on specific tables)

---

## 9) Summary: Databases as a Programmer’s Tool

From a programmer’s perspective, databases:

1. **Persist data** beyond the lifetime of a single program run
2. **Centralize shared state** for many users and processes
3. **Enforce correctness** through constraints and transactions
4. **Provide a query interface** (SQL) to ask for data without writing low-level file or storage logic

Applications connect via **drivers**, send **queries** (raw SQL, query builders, or ORM-generated), and receive **results**. The database handles storage, indexing, concurrency, and recovery.

Understanding how databases fit into programming—the purpose they serve and how they are used—makes it easier to design applications that are correct, scalable, and maintainable.

---

## Related materials

- [00 – Introduction](00-Introduction.md) — What is a database, and why were they developed?
- [04 – PostgreSQL](04-PostgreSQL.md) — Introduction to PostgreSQL
- [05 – SQL Fundamentals](05-SQL-fundamentals.md) — Building and querying with SQL
- [13 – Entity Framework Core](13-ORM-and-EF-Core.md) — A practical ORM for .NET applications
- [14 – Managing Users and Roles in Programming](14-Users-and-Roles-in-Programming.md) — Application-level users, roles, and database access
