# Assignment 3 — TrailShop: Stores, Stock, Indexes, and Roles

> [!NOTE]
> This assignment continues from **Assignment 2**. You must have the TrailShop database with `categories`, `products`, `customers`, `orders`, and `order_items` before starting.

> [!IMPORTANT]
> Copy the Assignment-3 folder with this Instructions.md file into your classroom repository.

Your classroom repository structure should look similar to this:

```md
your-Classroom-repo-name
├── Assignment-1
│ ├── 01_schema.sql
│ ├── 01_seed.sql
│ ├── 01_queries.sql
│ └── Instructions.md
├── Assignment-2
│ ├── 02_schema.sql
│ ├── 02_seed.sql
│ ├── 02_queries.sql
│ └── Instructions.md
├── Assignment-3
│ └── Instructions.md
├── Exercise-1 (optional)
├── Exercise-2
├── Exercise-3
├── Exercise-4
└── README.md
```

## Prerequisites

- Completed Assignment 2 (TrailShop database with customers and orders)
- Familiarity with [Materials 10 — Indexes and Indexing](./Materials/10-Indexes-and-Indexing.md)
- Familiarity with [Materials 11 — Users and Roles](./Materials/11-Users-and-Roles.md)

---

## Scenario

TrailShop is expanding into multiple stores. The team needs:

1. Store-specific stock tracking
2. Store employees
3. Performance improvements using indexes
4. Role-based access control for staff and analysts

---

# Part 1 — Add New Tables

Create **three new tables** with proper constraints and referential integrity. Interpret the requirements below into column definitions and constraints.

---

### Table: `stores`

TrailShop has one online store and two physical stores.

**Store requirements (interpret into columns + rules):**

- Each store has an **automatically generated numeric identifier**
- Each store has a **name** that must be unique
- Each store has a **type**: `ONLINE` or `PHYSICAL`
- Physical stores have a **city** and **street address**
- The online store does not have a physical address (allow NULLs for address fields)

---

### Table: `stocks`

Each store tracks its stock for each product.

**Stock requirements (interpret into columns + rules):**

- Each stock row links one **store** and one **product** (both required)
- A product may appear **only once per store** (use a composite primary key)
- Each stock row has a **quantity** (0 or higher)
- If a store is deleted, its stock rows should be deleted too
- We must **not** delete a product if it is referenced in any stock row

---

### Table: `employees`

Each employee belongs to one store.

**Employee requirements (interpret into columns + rules):**

- Each employee has an **automatically generated numeric identifier**
- Each employee has a **full name** (required)
- Each employee has a **role title** (required)
- Each employee belongs to one **store** (required)
- If a store has employees, we must **not** be able to delete that store

---

### Creation order

Create tables in dependency order:

1. `stores` (no foreign keys)
2. `stocks` (references stores and products)
3. `employees` (references stores)

---

### Deliverable

Add the `CREATE TABLE` statements to `03_schema.sql`.

---

# Part 2 — Insert Sample Data

Insert realistic test data so the team can practice queries and performance.

### Step 1 — Insert stores

Add **3 stores**:

| name               | type     | city     | street_address     |
| ------------------ | -------- | -------- | ------------------ |
| TrailShop Online   | ONLINE   | _(NULL)_ | _(NULL)_           |
| TrailShop Helsinki | PHYSICAL | Helsinki | Mannerheimintie 10 |
| TrailShop Kuopio   | PHYSICAL | Kuopio   | Puijonkatu 5       |

---

### Step 2 — Insert employees

Add **6 employees** (2 per store). Use correct `store_id` values (verify with `SELECT * FROM stores;`).

| full_name        | role_title      | hire_date  | store (name)       |
| ---------------- | --------------- | ---------- | ------------------ |
| Aino Laine       | Store Manager   | 2023-05-10 | TrailShop Online   |
| Mikko Saarinen   | Sales Support   | 2024-01-15 | TrailShop Online   |
| Ella Virtanen    | Store Manager   | 2022-09-01 | TrailShop Helsinki |
| Jari Lehtonen    | Sales Associate | 2023-11-20 | TrailShop Helsinki |
| Niko Hakkarainen | Store Manager   | 2021-04-12 | TrailShop Kuopio   |
| Salla Niemi      | Sales Associate | 2024-02-05 | TrailShop Kuopio   |

---

### Step 3 — Insert stocks

Insert stock rows for **at least 8 products** across the 3 stores.

Rules:

- Each store must have at least **5 products** in stock
- At least **2 products** must be available in **all three** stores
- Use realistic quantities (0 to 100)

---

### Deliverable

Create `03_seed.sql` with all INSERT statements for stores, employees, and stocks.

---

# Part 3 — Indexing

Create indexes to improve query performance. Refer to [Materials 10](./Materials/10-Indexes-and-Indexing.md) for guidance.

### Required indexes

1. **Stock lookup index** — Index `stocks` by `store_id` and `product_id` to speed up stock checks per store.
2. **Employee lookup index** — Index `employees` by `store_id` to speed up store staffing queries.
3. **Order lookup index** — Add an index on `orders(customer_id)` to speed up customer order history queries.
4. **Product name search index** — Add an index on `products(name)` to speed up product searches.

Use a separate file for indexes.

---

### Deliverable

Create `03_indexes.sql` with all `CREATE INDEX` statements.

---

# Part 4 — Users and Roles

Define roles and privileges for TrailShop staff. Refer to [Materials 11](./Materials/11-Users-and-Roles.md) for syntax.

### Required roles

1. **role_store_manager**
   - Can SELECT/INSERT/UPDATE on `stocks`
   - Can SELECT on `products`, `stores`, and `employees`
2. **role_sales_associate**
   - Can SELECT on `products` and `stocks`
3. **role_analyst**
   - Can SELECT on `customers`, `orders`, `order_items`, `products`, `stores`, `stocks`

### Required users

Create three users and assign roles:

- `manager1` → `role_store_manager`
- `sales1` → `role_sales_associate`
- `analyst1` → `role_analyst`

Set simple passwords for testing (for example: `manager1`, `sales1`, `analyst1`).

---

### Deliverable

Create `03_roles.sql` with all `CREATE ROLE`, `CREATE USER`, and `GRANT` statements.

---

# Part 5 — Queries

Write SQL queries that combine the new tables with existing ones.

### Required queries

1. **Store stock list** — Show each store name with product names and quantities. Order by store name, then product name.
2. **Low stock report** — Show products with total stock across all stores less than 10. Include product name and total quantity.
3. **Employees per store** — Show each store name and the number of employees. Include stores with zero employees (LEFT JOIN).
4. **Top stocked products** — Show the 5 products with the highest total stock across all stores.

---

### Deliverable

Create `03_queries.sql` with all 4 queries.

---

# Submission Requirements

Submit these files in the Assignment-3 folder:

- `03_schema.sql` — CREATE TABLE for stores, stocks, employees
- `03_seed.sql` — INSERT statements for stores, employees, stocks
- `03_indexes.sql` — CREATE INDEX statements
- `03_roles.sql` — CREATE ROLE/USER/GRANT statements
- `03_queries.sql` — All 4 queries

Your classroom repository should look like:

```md
your-Classroom-repo-name
├── Assignment-1
│ ├── 01_schema.sql
│ ├── 01_seed.sql
│ ├── 01_queries.sql
│ └── Instructions.md
├── Assignment-2
│ ├── 02_schema.sql
│ ├── 02_seed.sql
│ ├── 02_queries.sql
│ └── Instructions.md
├── Assignment-3
│ ├── 03_schema.sql (new)
│ ├── 03_seed.sql (new)
│ ├── 03_indexes.sql (new)
│ ├── 03_roles.sql (new)
│ ├── 03_queries.sql (new)
│ └── Instructions.md
├── Exercise-1
├── Exercise-2
├── Exercise-3
├── Exercise-4
└── README.md
```

---

# Self-check

Before submitting, verify:

1. Does `03_schema.sql` run without errors (assuming Assignment-1 and Assignment-2 tables exist)?
2. Does `03_seed.sql` insert all stores, employees, and stocks without errors?
3. Does `03_indexes.sql` create all indexes without errors?
4. Do the role and user commands in `03_roles.sql` run without errors?
5. Do queries 1 and 2 return results that match your inserted stock data?
