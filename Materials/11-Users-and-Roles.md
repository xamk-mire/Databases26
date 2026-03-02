# Users and Roles (PostgreSQL)

### Access control and permissions

This chapter introduces **database users and roles**:

- **Roles and users** — what they are in PostgreSQL
- **Privileges** — what can be granted or revoked
- **Schemas and ownership** — who owns objects
- **Common role patterns** — read-only vs. read-write access

---

# 1) Roles and users in PostgreSQL

PostgreSQL uses **roles** for access control.  
A role can act as a **user** (can log in) or just as a **group** of privileges.

- **Role** — an identity that can own objects and be granted privileges
- **Login role (user)** — a role with `LOGIN` that can connect
- **Group role** — a role without `LOGIN`, used to collect privileges

Roles can also be **members** of other roles. This is how PostgreSQL supports group permissions:

- A login role (user) can inherit privileges from one or more group roles.
- Group roles can be nested (e.g. `app_write` includes `app_read`).

---

## Example: user vs. role (conceptual)

- `app_read` — group role with read-only privileges
- `app_write` — group role with read/write privileges
- `alice` — login role (user)

You grant group roles to users:

```sql
GRANT app_read TO alice;
GRANT app_write TO alice;
```

Now `alice` can read and write based on the privileges attached to those roles.

---

## Role attributes

Roles can have attributes that control what they are allowed to do. The most common are:

- **LOGIN** — can connect to the database (makes the role a user)
- **CREATEDB** — can create databases
- **CREATEROLE** — can create/alter other roles

In beginner-level work, you usually avoid `CREATEDB` and `CREATEROLE` except for admin tasks.

---

## Ownership vs. privileges

- **Ownership** means the role created the object (table, schema, function, etc.). Owners can always alter or drop their objects.
- **Privileges** (grants) allow access to objects owned by someone else.

This is why a common pattern is:

1. Create objects as an admin role
2. Grant only the needed privileges to app/user roles

---

## In practice

- Create **group roles** for permissions (e.g. `app_read`, `app_write`)
- Create **login roles** for people or applications
- Grant group roles to login roles

This keeps access control simple and easier to maintain.

---

# 2) Creating roles and users

PostgreSQL creates **roles** with `CREATE ROLE`.  
There is no separate `CREATE USER` in PostgreSQL (it exists as an alias for `CREATE ROLE ... LOGIN`).

When you create a role, you decide whether it can log in and which attributes it has.

---

## Create a login role (user)

```sql
CREATE ROLE alice LOGIN PASSWORD 'secret';
```

This creates a role named `alice` that can log in with a password `secret`.  
In a real system, use a strong password and store it securely.

---

## Create a group role

```sql
CREATE ROLE app_read;
CREATE ROLE app_write;
```

Group roles do not have `LOGIN`, so they cannot connect directly. They are used to **collect privileges**.

### Example: Create read-only and read-write group roles

```sql
-- Create the roles (no LOGIN)
CREATE ROLE app_read;
CREATE ROLE app_write;

-- Allow usage of the schema
GRANT USAGE ON SCHEMA public TO app_read;
GRANT USAGE ON SCHEMA public TO app_write;

-- Read-only access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read;

-- Read-write access
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_write;
```

To include future tables, set default privileges:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO app_read;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_write;
```

---

## Grant group roles to a user

```sql
GRANT app_read TO alice;
GRANT app_write TO alice;
```

Now `alice` inherits permissions from `app_read` and `app_write`.

---

## Create a login role with attributes

You can add role attributes directly:

```sql
CREATE ROLE app_admin
  LOGIN
  PASSWORD 'secret'
  CREATEDB
  CREATEROLE;
```

Common attributes:

- `LOGIN` / `NOLOGIN`
- `CREATEDB` / `NOCREATEDB`
- `CREATEROLE` / `NOCREATEROLE`
- `SUPERUSER` / `NOSUPERUSER` (avoid for normal users)

---

## Modify existing roles

Change password:

```sql
ALTER ROLE alice PASSWORD 'new_secret';
```

Grant or revoke login:

```sql
ALTER ROLE alice LOGIN;
-- or
ALTER ROLE alice NOLOGIN;
```

Add role attributes:

```sql
ALTER ROLE alice CREATEDB;
```

---

## Drop roles

```sql
DROP ROLE alice;
```

You can only drop a role if it:

- does not own database objects, and
- is not required by other roles

## If a role owns objects, you must reassign ownership or drop those objects first.

# 3) Privileges (GRANT and REVOKE)

Privileges control what a role can do.

Common privileges:

- **SELECT** — read rows
- **INSERT** — add rows
- **UPDATE** — modify rows
- **DELETE** — remove rows
- **USAGE** (on schema) — use objects inside a schema
- **CREATE** (on schema) — create objects in a schema

---

# 3.1) Example: University database roles (database-specific)

This example shows how to set up roles for the **university database** tables:
`students`, `courses`, `enrollments`, `grades`, `teachers`.

Goal:

- **uni_read** → read-only access to all university tables
- **uni_write** → read/write access to all university tables
- **uni_admin** → can create/alter/drop objects in the schema
- All of the above **only** connect to the **university** database

### Step 1 — Create group roles

```sql
CREATE ROLE uni_read;
CREATE ROLE uni_write;
CREATE ROLE uni_admin;
```

### Step 2 — Restrict database access

PostgreSQL roles exist at the **cluster** level, so you restrict access by database privileges.
Assume your database is named `university_db`.

```sql
-- Remove default public access (optional but recommended)
REVOKE CONNECT ON DATABASE university_db FROM PUBLIC;

-- Allow only our university roles to connect
GRANT CONNECT ON DATABASE university_db TO uni_read;
GRANT CONNECT ON DATABASE university_db TO uni_write;
GRANT CONNECT ON DATABASE university_db TO uni_admin;
```

Now these roles can connect only to `university_db`. Other databases remain inaccessible unless explicitly granted.

---

### Step 3 — Grant schema usage

Assuming the tables are in `public`:

```sql
GRANT USAGE ON SCHEMA public TO uni_read;
GRANT USAGE ON SCHEMA public TO uni_write;
GRANT USAGE, CREATE ON SCHEMA public TO uni_admin;
```

### Step 4 — Grant table privileges

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public TO uni_read;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public TO uni_write;
```

### Step 5 — Default privileges for future tables

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO uni_read;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO uni_write;
```

### Step 6 — Create login users and assign roles

```sql
CREATE ROLE uni_student LOGIN PASSWORD 'secret';
CREATE ROLE uni_teacher LOGIN PASSWORD 'secret';
CREATE ROLE uni_admin_user LOGIN PASSWORD 'secret';

GRANT uni_read TO uni_student;
GRANT uni_write TO uni_teacher;
GRANT uni_admin TO uni_admin_user;
```

### Explanation

- **uni_student** can read university data but cannot modify it.
- **uni_teacher** can read and update data (e.g. add grades).
- **uni_admin_user** can create or change tables in the schema.

---

## Example: read-only role

```sql
-- Allow usage of the public schema
GRANT USAGE ON SCHEMA public TO app_read;

-- Allow read access to all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read;
```

---

## Example: limit access to specific tables (uni_student)

If you want a role to read **only** certain tables, grant SELECT on those tables only.

Example goal:

- `uni_student` can read **students**, **courses**, and **grades**
- `uni_student` cannot read **enrollments** or **teachers**

```sql
-- Allow schema usage
GRANT USAGE ON SCHEMA public TO uni_student;

-- Grant SELECT only on specific tables
GRANT SELECT ON TABLE students, courses, grades TO uni_student;

-- (Optional) revoke wider access if it was granted earlier
REVOKE SELECT ON ALL TABLES IN SCHEMA public FROM uni_student;
```

If you want future tables to be restricted, do **not** grant default privileges broadly.

---

## Example: read-write role

```sql
GRANT USAGE ON SCHEMA public TO app_write;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_write;
```

---

# 4) Default privileges

When you grant privileges on existing tables, **new tables are not included automatically**.  
To make future tables use the same privileges, set **default privileges**:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO app_read;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_write;
```

These default privileges apply to objects created **by the role that runs the ALTER DEFAULT PRIVILEGES command**.

---

# 5) Ownership and schemas

Every database object has an **owner** (a role). The owner can:

- change privileges
- alter or drop the object

Schemas are namespaces (like folders).  
Common setups:

- Keep tables in `public`
- Create app-specific schemas (e.g. `app`)

Example:

```sql
CREATE SCHEMA app AUTHORIZATION alice;
```

---

# 6) Common role patterns

### Pattern A: Read-only and read-write

- `app_read` → SELECT only
- `app_write` → SELECT + INSERT + UPDATE + DELETE
- Assign users to one or both roles

### Pattern B: Separate admin role

- `app_admin` → can CREATE, ALTER, DROP
- `app_read` / `app_write` → data access

---

# 7) Good practices

- **Least privilege** — give only what is needed
- **Use group roles** — easier to manage than per-user grants
- **Document** what each role can do
- **Avoid using superuser** for normal work

---

# 8) Quick checklist

Before deploying a database:

1. Create group roles (`app_read`, `app_write`)
2. Grant schema usage and table privileges
3. Set default privileges for future tables
4. Create login roles and assign groups
5. Test with a read-only user

---

## 9) Testing privileges (hands-on)

After creating roles and grants, you should **test** that access works as expected.  
The simplest way is to connect as each role and try both allowed and disallowed actions.

### A) Test as a read-only user (PowerShell/terminal or SQL shell)

**Option 1 — PowerShell/terminal → psql**

> Make sure that the psql is added in the path -> otherwise your system might not be able to recognize the command

```
psql -U uni_student -d university_db
```

**Option 2 — SQL shell (psql)**

If you are already in `psql`, connect as the user:

```
\c university_db uni_student
```

Then run a **SELECT** (should succeed):

```sql
SELECT * FROM students;
```

3. Try an **INSERT** (should fail):

```sql
INSERT INTO students (full_name, email) VALUES ('Test User', 'test@uni.fi');
```

Expected result: permission denied for table `students`.

---

### B) Test as a read-write user (PowerShell/terminal or SQL shell)

**Option 1 — PowerShell/terminal → psql**

```
psql -U uni_teacher -d university_db
```

**Option 2 — SQL shell (psql)**

If you are already in `psql`, connect as the user:

```
\c university_db uni_teacher
```

Then run a **SELECT** (should succeed):

```sql
SELECT * FROM courses;
```

3. Run an **UPDATE** (should succeed):

```sql
UPDATE courses SET credits = credits + 1 WHERE course_id = 1;
```

4. Run a **DELETE** (should succeed if granted):

```sql
DELETE FROM enrollments WHERE student_id = 1 AND course_id = 2;
```

---

### C) Test database access only (PowerShell/terminal or SQL shell)

If you restricted database access (e.g. `REVOKE CONNECT FROM PUBLIC`), confirm that a role **without** CONNECT cannot log in:

Create a new test user (`test_user`)

```sql
CREATE ROLE test_user LOGIN PASSWORD 'test';
```

**Option 1 — PowerShell/terminal → psql**

```
psql -U test_user -d university_db
```

**Option 2 — SQL shell (psql)**

If you are already in `psql`, try connecting:

```
\c university_db test_user
```

Expected result: permission denied for database `university_db`.

---

### Tip: check grants inside SQL

PostgreSQL provides helper functions to check privileges:

```sql
SELECT has_table_privilege('uni_student', 'students', 'SELECT');
SELECT has_table_privilege('uni_student', 'students', 'INSERT');
```

These return `true` or `false`.

---

## Summary

| Topic          | Key ideas                                                                               |
| -------------- | --------------------------------------------------------------------------------------- |
| **Roles**      | Roles are identities; login roles are users; group roles collect privileges.            |
| **Privileges** | GRANT/REVOKE control SELECT/INSERT/UPDATE/DELETE and schema usage.                      |
| **Ownership**  | Owners can alter or drop objects; schemas group objects.                                |
| **Patterns**   | Read-only vs. read-write roles; separate admin roles.                                   |
| **Defaults**   | Default privileges control access to future objects.                                    |
| **Testing**    | Verify privileges by connecting as each role and attempting allowed/disallowed actions. |

---

_End of Materials 11._
