# Glossary of Database Terminology

A glossary of database terms used in the course materials. Terms are listed alphabetically.

**★ = Key term** — Essential concepts to master.

---

## Key Terms


| Domain               | Key terms to know                                           |
| -------------------- | ----------------------------------------------------------- |
| **Foundations**      | Database, Data, Table, Row, Column, Schema, SQL             |
| **Data modelling**   | Entity, Attribute, Relationship, ER diagram, Cardinality    |
| **Keys & integrity** | Primary key, Foreign key, Constraint, Referential integrity |
| **Normalization**    | 1NF, 2NF, 3NF, Redundancy, Junction table                   |
| **SQL basics**       | SELECT, INSERT, UPDATE, DELETE, WHERE, JOIN, CRUD           |
| **Joins**            | INNER JOIN, LEFT JOIN                                       |
| **Aggregation**      | GROUP BY, HAVING, Aggregate function                        |
| **Transactions**     | Transaction, ACID, COMMIT, ROLLBACK                         |
| **Indexing**         | Index, Primary key index                                    |
| **Security**         | Role, Privilege, GRANT, Authentication, Authorization       |


---

## A

**ACID** ★ — A set of guarantees for transactions: *Atomicity* (all-or-nothing), *Consistency* (database moves between valid states), *Isolation* (concurrent transactions don't interfere), and *Durability* (committed changes survive crashes).

**Ad-hoc querying** — Asking new questions on the fly without pre-built code paths or reports. Relational databases make this practical via SQL and query optimization.

**Aggregate function** ★ — A function that summarizes multiple rows into a single value (e.g., `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`). Used with `GROUP BY` to summarize each group.

**Application user** — A person or system who uses your application (e.g., Alice, Bob). Stored as rows in application tables like `Users`. Distinguished from *database users*, which are identities used to connect to the database.

**Associative entity** — An entity that represents a relationship between two or more entities. Often implemented as a junction table (e.g., `Enrollment` linking Student and Course).

**Atomic value** — A single value in a cell—not a list, nested structure, or repeating group. Required for First Normal Form (1NF).

**Atomicity** — A transaction property: either all statements in the transaction are applied, or none are. No partial commits.

**Attribute** ★ — In data modelling: a property that describes an entity. In the relational model: a named column in a relation. Examples: `student_id`, `name`, `email`.

**Authentication** ★ — The process of verifying identity ("Who is this request from?"). Typically done via email/password, with sessions or tokens created on success.

**Authorization** ★ — The process of checking whether an authenticated user is allowed to perform an action ("What can you do?"). Often implemented via role-based access control.

---

## B

**B-tree** — A common index structure that keeps keys in sorted order. Great for equality lookups, range queries, and general-purpose OLTP. Default index type in PostgreSQL.

**BEGIN** — SQL keyword to start a transaction. Everything until `COMMIT` or `ROLLBACK` is one unit of work.

**Bridge table** — See *Junction table*.

**Business logic** — The layer of an application that applies domain rules (e.g., "can this user place this order?"). Sits between presentation and data access.

---

## C

**CASCADE** — An `ON DELETE` or `ON UPDATE` action on a foreign key. When the parent row is deleted or updated, child rows are automatically deleted or updated accordingly.

**Candidate key** — A column or group of columns that could uniquely identify rows in a table. The primary key is chosen from among candidate keys.

**Cardinality** ★ — The "how many" of a relationship: one-to-one (1:1), one-to-many (1:N), or many-to-many (M:N).

**CHECK constraint** — A database rule that values must satisfy a boolean expression (e.g., `credits BETWEEN 1 AND 20`).

**Column** ★ — A vertical set of values in a table representing one attribute. In the relational model, synonymous with *attribute*.

**Columnar storage** — Data stored by column rather than by row. Good for OLAP because queries often read a few columns over many rows and aggregate them; also compresses well.

**COMMIT** ★ — SQL keyword to end a transaction and make all changes permanent.

**Composite key** — A primary or unique key consisting of two or more columns (e.g., `(student_id, course_id)` in an enrollments table).

**Composite index** — An index on multiple columns. Order matters: leftmost columns are most useful. Helps when queries filter on the indexed columns in order.

**Conceptual data model** — The highest level of data modelling: captures main concepts and relationships in a domain without implementation details. Does not specify primary keys, data types, or tables.

**Concurrency control** — Mechanisms that keep transactions correct when many run simultaneously. Common approaches: locking and MVCC.

**Connection pool** — A set of reusable database connections so applications don't open and close a new connection for every query.

**Connection string** — Parameters that identify the database and how to reach it (e.g., `postgresql://username:password@hostname:5432/database_name`).

**Consistency** — An ACID property: the database enforces constraints so that after every committed transaction, the database is in a valid state.

**Constraint** ★ — A rule the database enforces to keep data clean and meaningful (e.g., PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK, DEFAULT).

**CRUD** ★ — The four basic operations: *Create* (INSERT), *Read* (SELECT), *Update* (UPDATE), *Delete* (DELETE).

**Crow's Foot notation** — A compact ER diagram style widely used in industry. Uses crow's foot symbols for "many" and single lines for "one."

---

## D

**Data** ★ — Recorded representations of facts or observations, stored in a structured form so a system can retrieve, validate, relate, and process them reliably.

**Data access layer** — The part of an application that sends queries to the database and maps results to application objects.

**Data model** — The structure and rules for how data is organized (tables, documents, graphs, etc.).

**Data type** — The kind of value a column can hold (e.g., INTEGER, VARCHAR, DATE, BOOLEAN).

**Data warehouse** — A system optimized for OLAP, often containing cleaned/combined historical data from multiple sources. The "single place" for analytics.

**Database** ★ — A managed collection of persistent data plus mechanisms and rules for storing, retrieving, and keeping it correct and secure. In strict terms: the structured data itself (distinct from DBMS).

**Database driver** — A library that speaks the database's protocol (e.g., `pg` for Node.js, `psycopg2` for Python, Npgsql for .NET).

**Database user** — An identity used to connect to the database (e.g., `app_user`, `uni_read`). Lives in database system catalogs. Distinguished from *application users*.

**DbContext** — In Entity Framework Core: the central object representing a session with the database. Manages connections, tracks entities, translates LINQ to SQL, and executes SaveChanges.

**DbSet** — In Entity Framework Core: a typed collection representing a table (e.g., `DbSet<Student>` for the Students table).

**DDL** — Data Definition Language. SQL statements that define structure (CREATE TABLE, ALTER TABLE, DROP TABLE, etc.).

**Declarative query** — Specifying the desired result, not the step-by-step procedure. Opposite of navigational/procedural access. SQL is declarative.

**DELETE** ★ — SQL statement that removes rows from a table. Uses `WHERE` to specify which rows. Omitting WHERE deletes all rows.

**Delete anomaly** — A normalization problem: deleting one fact accidentally removes another (e.g., deleting the last order for a customer removes the customer record).

**Denormalization** — Intentionally introducing redundancy to simplify queries or improve performance. A trade-off: you accept extra maintenance for benefits elsewhere.

**Derived attribute** — An attribute calculated from other data (e.g., age derived from date_of_birth). Avoids redundancy and inconsistency.

**DML** — Data Manipulation Language. SQL statements that modify data (INSERT, UPDATE, DELETE, SELECT).

**Domain** — The set of values an attribute is allowed to take. Enforced via data types and constraints.

**Durability** — An ACID property: once a transaction is committed, its changes survive crashes and power loss (via logging, replication, etc.).

---

## E

**Entity** ★ — A real-world object or concept that can be uniquely identified and has meaningful data associated with it. Examples: Customer, Order, Product, Student.

**Entity Framework Core (EF Core)** — Microsoft's ORM for .NET. Maps C# classes to database tables, generates SQL from LINQ, and supports migrations.

**Entity instance** — A specific occurrence of an entity (e.g., Student #1001: Alice). In databases, rows represent entity instances.

**Entity type** — The general category of an entity (e.g., Student). In databases, tables represent entity types.

**ER diagram** ★ — Entity-Relationship diagram. A graphical model of a system's data structure showing entities, attributes, relationships, cardinality, and optionality.

**EXPLAIN** — PostgreSQL command that shows the query plan—the steps the database will use to execute a query. Does not run the query.

**EXPLAIN ANALYZE** — Like EXPLAIN, but actually executes the query and reports real timings and row counts.

---

## F

**Filtering** — Selecting which rows appear in query results. Done with the `WHERE` clause.

**First Normal Form (1NF)** ★ — A table is in 1NF if: (1) each cell contains a single atomic value, (2) each row is uniquely identified, (3) each column has one meaning and one data type. No repeating groups.

**Fluent API** — In EF Core: a programmatic way to configure entities and relationships in `OnModelCreating`, as an alternative to data annotations.

**Foreign key (FK)** ★ — A column in one table that references the primary key in another table. Enforces referential integrity: you cannot reference something that does not exist.

**Full outer join** — A JOIN type that keeps all rows from both tables. Where there is no match, the other side's columns are NULL.

**Functional index** — An index built on an expression (e.g., `LOWER(email)`) rather than a raw column. Useful when queries use functions in the WHERE clause.

---

## G

**GROUP BY** ★ — SQL clause that forms groups of rows based on equal values in one or more columns. Aggregate functions then summarize each group.

**Group role** — In PostgreSQL: a role without LOGIN, used to collect privileges. Users inherit privileges by being granted group roles.

**GRANT** ★ — SQL statement that gives privileges (SELECT, INSERT, UPDATE, DELETE, USAGE, etc.) to a role.

---

## H

**HAVING** ★ — SQL clause that filters *groups* after aggregation. Unlike WHERE, which filters rows before grouping.

**Horizontal scaling (scale out)** — Increasing capacity by adding more machines and distributing data/work across them.

**Hash index** — An index type optimized for equality lookups. Less common than B-tree in PostgreSQL for general use.

---

## I

**Identifier** — In SQL: names of tables and columns. In data modelling: a value that uniquely identifies an entity instance.

**Identity** — In PostgreSQL: a mechanism for auto-generating numeric IDs (`GENERATED ALWAYS AS IDENTITY` or `GENERATED BY DEFAULT AS IDENTITY`).

**Impedance mismatch** — The disconnect between relational databases (tables, rows, columns) and object-oriented programming (objects, properties, references). ORMs address this.

**Index** ★ — A separate data structure that speeds up lookups. Stores index keys and pointers to table rows. Like a book's index. Common types: B-tree, hash, GIN, GiST.

**Index-only scan** — When a query can be answered entirely from the index, PostgreSQL can avoid reading the table. Also called *covering index scan*.

**INNER JOIN** ★ — A JOIN type that returns only rows where the join condition is true in both tables. Non-matching rows are excluded.

**Insert anomaly** — A normalization problem: you cannot record a valid fact until another fact exists, or you must invent/duplicate data.

**Instance** — The current contents of a table (the data right now). Distinguished from *schema*, which is the stable structure.

**Isolation** — An ACID property: concurrent transactions don't see each other's uncommitted changes in ways that break guarantees. Depends on isolation level.

**Isolation level** — The "strength" of isolation (e.g., read committed, repeatable read, serializable). Trade correctness vs. performance.

---

## J

**JOIN** ★ — A SQL operation that combines rows from two or more tables based on a relationship between them. Types: INNER, LEFT, RIGHT, FULL OUTER.

**Junction table** ★ — A table that implements a many-to-many relationship by containing foreign keys to both related tables. Also called *bridge table* or *associative table*. Example: `Enrollments(student_id, course_id)`.

---

## K

**Key** — A column or group of columns that identifies rows. See *primary key*, *foreign key*, *candidate key*, *composite key*.

**Keyword** — In SQL: command words such as CREATE, INSERT, SELECT, WHERE.

---

## L

**LEFT JOIN (LEFT OUTER JOIN)** ★ — A JOIN type that keeps all rows from the left table and matching rows from the right. Where there is no match, the right table's columns are NULL.

**Least privilege** — A security principle: grant only the permissions needed, nothing more.

**Literal** — In SQL: actual values, like `'Aino'` or `5`.

**Logical data model** — The middle level of data modelling: defines entities, attributes, primary keys, relationships, and cardinality. ER diagrams are typically used. Remains independent of any specific database system.

**Logical operators** — AND, OR, NOT. Used to combine conditions in WHERE clauses.

**Login role** — In PostgreSQL: a role with LOGIN that can connect to the database. Essentially a "user" in everyday terms.

---

## M

**Mandatory participation** — A relationship constraint: the entity must participate (e.g., every Employee must belong to a Department). In the database: foreign key is NOT NULL.

**Materialized view** — A stored result of a query, like a cached table. Refreshed periodically. Very fast reads; may be stale until refresh.

**Metadata** — Data about data: describes what stored data means, how it is structured, where it came from, and how it should be handled.

**Migration** — In EF Core: a versioned schema change. Migrations are code files that create or alter the database structure. Applied with `dotnet ef database update`.

**Multi-valued attribute** — An attribute that can have multiple values per entity (e.g., phone_numbers). In relational databases, typically converted to a separate table.

**MVCC** — Multi-Version Concurrency Control. Readers see a consistent snapshot while writers create new versions. Readers don't block writers, and writers don't block readers as aggressively as with locking.

---

## N

**Navigation property** — In EF Core: a property on an entity that references a related entity (e.g., `Student.Enrollments`). Used with `.Include()` to load related data.

**NoSQL** — A family of database models (key-value, document, wide-column, graph) that often prioritize flexibility, scale, or specific access patterns over strict relational guarantees. "Not Only SQL."

**Normalization** ★ — The process of restructuring tables to remove redundancy and anomalies (update, insert, delete). Achieved by splitting data into more tables and linking with keys.

**NOT NULL** — A constraint: the column cannot contain NULL. Every row must have a value.

**Null** ★ — A special value meaning "missing" or "unknown." Distinct from empty string or zero. Comparisons with NULL yield unknown (not true or false).

---

## O

**OLAP** — Online Analytical Processing. Workloads focused on large scans and aggregations across lots of data (dashboards, trend analysis, "sales by region over 5 years").

**OLTP** — Online Transaction Processing. Workloads focused on many small, frequent transactions (placing orders, updating accounts).

**Optional participation** — A relationship constraint: the entity may or may not participate (e.g., a Student may or may not have a Mentor). In the database: foreign key can be NULL.

**ORM** — Object-Relational Mapper. A library that maps database tables to programming-language objects. Generates SQL from object-oriented or LINQ-style code. Examples: Entity Framework Core, Hibernate, SQLAlchemy.

**Orphaned record** — A row whose foreign key references a non-existent parent row. Foreign key constraints prevent this.

**Ownership** — In PostgreSQL: the role that created an object (table, schema, etc.). Owners can alter or drop their objects. Distinguished from privileges (grants).

---

## P

**Parameterized query** — A query that uses placeholders (e.g., `%s`, `$1`) for values instead of string concatenation. Prevents SQL injection and allows query optimization.

**Partial dependency** — A 2NF violation: a non-key attribute depends on only part of a composite primary key. Causes redundancy.

**Partial index** — An index that stores only rows matching a condition. Smaller and faster when you always query a subset.

**Password hashing** — One-way transformation of passwords before storage. Use bcrypt, Argon2, or PBKDF2. Never store plaintext passwords.

**Persistence** — Data surviving program restarts, server reboots, and power loss. A core benefit of databases.

**Physical data model** — The lowest level of data modelling: actual implementation with tables, column types, foreign keys, constraints, indexes. The SQL DDL.

**Polyglot persistence** — Using different databases for different needs (e.g., relational for transactions, search engine for full-text, cache for performance).

**Primary key (PK)** ★ — The main identifier for rows in a table. Must be unique, NOT NULL, stable, and minimal. Only one per table (can be composite).

**Privilege** ★ — A permission granted to a role (SELECT, INSERT, UPDATE, DELETE, USAGE, CREATE). Controlled by GRANT and REVOKE.

---

## Q

**Query optimizer / Query planner** — The database component that decides *how* to execute a query (join order, index usage, parallelism). Enables declarative SQL to be efficient.

**Query plan** — The steps the database will use to execute a query. Shown by EXPLAIN.

---

## R

**RBAC** — Role-Based Access Control. Authorization based on user roles; each role implies a set of permissions.

**RDBMS** — Relational Database Management System. A system that stores data in tables and supports SQL (e.g., PostgreSQL, MySQL).

**Record** — See *Row*.

**Recovery** — Restoring the database to a consistent state after a crash. Achieved via logging (e.g., WAL in PostgreSQL).

**Redundancy** ★ — Storing the same fact in more than one place. Can cause update, insert, and delete anomalies.

**REFERENCES** — SQL keyword that creates a foreign key. Ensures the column value exists in the referenced table.

**Referential integrity** ★ — The rule that every foreign key value must point to an existing row in the referenced table (or be NULL if allowed). Enforced automatically by the database.

**Relation** ★ — In the relational model: a table. A collection of structured facts about a certain kind of thing. Has a name, attributes (columns), and tuples (rows).

**Relational model** ★ — The design philosophy and mathematical framework behind relational databases. Treats data as relations (tables) with keys, constraints, and logic-based operations. Introduced by E. F. Codd.

**Relationship** ★ — A connection between two entities. Describes how they are related (e.g., Student takes Course). Has cardinality and optionality.

**REVOKE** — SQL statement that removes privileges from a role.

**Right join** — Same as LEFT JOIN but keeps all rows from the right table. Rarely needed; can be rewritten by swapping tables.

**ROLLBACK** ★ — SQL keyword to end a transaction and discard all changes made in it.

**Role** ★ — In PostgreSQL: an identity that can own objects and be granted privileges. Can be a login role (user) or a group role.

**Row** ★ — A single record in a table. In the relational model, synonymous with *tuple*. Represents one entity instance.

---

## S

**Savepoint** — A named point within a transaction. You can roll back to a savepoint without rolling back the whole transaction.

**Schema** ★ — (1) The structure of a database: tables, columns, constraints, etc. (2) In PostgreSQL: a namespace for organizing objects (e.g., `public`). Like a folder.

**Second Normal Form (2NF)** ★ — A table is in 2NF if it is in 1NF and has no partial dependency: every non-key attribute depends on the *whole* primary key.

**SELECT** ★ — SQL statement that reads data from tables. Can filter (WHERE), sort (ORDER BY), aggregate (COUNT, SUM, etc.), and group (GROUP BY).

**Selectivity** — How many rows share the same value. High selectivity (e.g., unique email) → good for indexes. Low selectivity (e.g., grade 0–5) → index may not help.

**Self-join** — Joining a table to itself. Uses different aliases for the "left" and "right" copies. Common for hierarchies (e.g., employees and managers).

**Sequence** — A database object that generates unique numeric values. Used for auto-incrementing IDs.

**Sequential scan (Seq Scan)** — Reading every row in a table and filtering. Opposite of index scan. Used when an index wouldn't help or doesn't exist.

**SET NULL** — An ON DELETE or ON UPDATE action: set the foreign key to NULL in child rows when the parent is deleted/updated. Requires nullable FK column.

**Single-valued attribute** — An attribute with one value per entity (e.g., birth_date).

**SQL** ★ — Structured Query Language. A declarative language for querying and manipulating relational data. You describe *what* you want; the database decides *how* to execute it.

**SQL injection** — A security vulnerability where malicious input is concatenated into SQL and executed. Prevented by parameterized queries.

**Statement** — One complete SQL instruction ending with `;`.

**Subquery** — A query nested inside another query. Can be used in WHERE, FROM, or SELECT.

**Surrogate key** — An artificially generated identifier (e.g., auto-increment ID) with no business meaning. Preferred over natural keys when natural keys can change.

**System of record** — The authoritative source of truth for some domain (e.g., payments ledger, orders). Demands strong correctness guarantees and auditability.

---

## T

**Table** ★ — A structured collection of rows and columns. The primary storage structure in relational databases. Represents a relation.

**Ternary relationship** — A relationship involving three entities (e.g., Doctor treats Patient in Hospital). More complex; often needs a junction table.

**Third Normal Form (3NF)** ★ — A table is in 3NF if it is in 2NF and has no transitive dependency: no non-key attribute depends on another non-key attribute.

**Token** — A credential (e.g., JWT) that identifies the user for subsequent requests after authentication. Alternative to session cookies.

**Transaction** ★ — A logical unit of work: one or more SQL statements treated as a single unit. Either all succeed or none do. Controlled by BEGIN, COMMIT, ROLLBACK.

**Transitive dependency** — A 3NF violation: a non-key attribute depends on another non-key attribute (e.g., teacher_name depends on teacher_id, which depends on course_id).

**Tuple** — In the relational model: a row. One complete record in a relation. Contains one value for each attribute.

**Type** — See *Data type*.

---

## U

**UNIQUE** — A constraint: no two rows may have the same value(s) in the constrained column(s).

**Unique index** — An index that enforces uniqueness. Created automatically for PRIMARY KEY and UNIQUE constraints.

**Update anomaly** — A normalization problem: if the same fact is stored in many rows, updating it in one place leaves others outdated. Leads to inconsistent data.

**UPDATE** ★ — SQL statement that changes existing rows. Uses SET for new values and WHERE to specify which rows. Omitting WHERE updates all rows.

**User** — In PostgreSQL: a role with LOGIN that can connect. In application context: an application user (stored in your tables).

**USING** — SQL clause in JOINs when both tables have the same column name for the join. Shorthand for ON left.col = right.col.

---

## V

**Vertical scaling (scale up)** — Increasing capacity by making one machine bigger (more CPU, RAM, faster disk).

**View** — A stored "window" into data—a saved query. Acts like a virtual table. Can simplify queries and control access.

---

## W

**WAL** — Write-Ahead Logging. PostgreSQL records changes to a log before applying them to data files. Enables durability and recovery.

**WHERE** ★ — SQL clause that filters which rows are included in the result. Applied before GROUP BY.

**Wildcard** — In pattern matching: `%` (any length) and `_` (single character) in LIKE expressions.

---

## Related Materials

This glossary covers terms from:

- 00 – Introduction
- 01 – Data Modelling
- 02 – ER Diagrams
- 03 – Relational Database
- 04 – PostgreSQL
- 05–07 – SQL Fundamentals
- 08 – Normalization and Schema Quality
- 09 – Transactions and Data Modification
- 10 – Indexes and Indexing
- 11 – Users and Roles
- 12 – Databases in Programming
- 13 – ORM and EF Core
- 14 – Managing Users and Roles in Programming
- 99 – Common Misconceptions

