# Assignment 2 — TrailShop: Customers, Orders, and JOINs

> [!NOTE]
> This assignment continues from **Assignment 1**. You must have completed the trailshop database (categories and products) before starting.

> [!IMPORTANT]
> Copy the Assignment-2 folder with this Instructions.md file into your classroom repository.

Your classroom repository structure should look similar to this:

```md
your-Classroom-repo-name
├── Assignment-1
│ ├── 01_schema.sql
│ ├── 01_seed.sql
│ ├── 01_queries.sql
│ └── Instructions.md
├── Assignment-2
│ └── Instructions.md
├── Exercise-1 (optional)
├── Exercise-2
└── README.md
```

## Prerequisites

- Completed Assignment 1 (trailshop database with `categories` and `products` tables)
- Familiarity with [Materials 07 — SQL Fundamentals Part III](../../Materials/07-SQL-fundamentals-3.md): JOINs, referential integrity, and constraints

---

## Scenario

TrailShop’s database is growing. The team now needs to support **customers** and **orders**. Your job is to:

1. Add foreign key constraints to the existing `products` table (referencing `categories`)
2. Create three new tables: `customers`, `orders`, and `order_items`
3. Insert sample data and write JOIN queries to combine data across tables

---

# Part 1 — Add Foreign Key to Products

In Assignment 1, `products` had a `category_id` column but **no foreign key constraint**. Now add it.

### Requirements

- Add a foreign key constraint so that `products.category_id` references `categories(category_id)`
- Use `ON DELETE RESTRICT` (the default) — we do not want to delete a category if products still reference it

### Deliverable

Create or update your schema file. You can either:

- Add an `ALTER TABLE` statement to a new file `02_schema.sql`

**Example pattern (from Materials 07 — university schema):** If `enrollments` had `student_id` without a foreign key, you would add:

```sql
ALTER TABLE enrollments
  ADD CONSTRAINT fk_enrollments_student
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT;
```

For TrailShop, apply the same pattern to `products` and `categories`.

---

# Part 2 — Create the New Tables

Create three new tables with proper constraints and referential integrity. Interpret the requirements below into column definitions and constraints.

---

### Table: `customers`

TrailShop needs to store customer information.

**Customer requirements (interpret into columns + rules):**

- Each customer has an **automatically generated numeric identifier**
- Each customer has a **full name**, which must always exist
- Each customer may have an **email**; two customers are not allowed to share the same email
- Email may be missing for some customers

---

### Table: `orders`

Each order belongs to one customer and records when the order was placed.

**Order requirements (interpret into columns + rules):**

- Each order has an **automatically generated numeric identifier**
- Each order must store which customer placed it (**customer_id**)
- Each order must have an **order date**
- If a customer has orders, we must **not** be able to delete that customer — use correct constraint on the foreign key

---

### Table: `order_items`

Each order contains one or more products. `order_items` is a junction table linking `orders` and `products`. Each row represents one product in one order, with a quantity and the price at the time of purchase.

**Order item requirements (interpret into columns + rules):**

- Each order item links one **order** and one **product** (both required)
- Each order item has a **quantity** (at least 1)
- Each order item stores the **unit price** at the time of the order as a decimal value (use NUMERIC or DECIMAL)
- A product may appear only once per order — use a composite primary key `(order_id, product_id)`
- When an order is deleted, its order items should be deleted too — use correct constraint on the order reference
- We must **not** delete a product if it is referenced in any order item — use correct constraint on the product reference

---

### Creation order

Create tables in dependency order:

1. `customers` (no foreign keys)
2. `orders` (references customers)
3. `order_items` (references orders and products)

---

### Deliverable

Add the `CREATE TABLE` statements to `02_schema.sql`.

---

# Part 3 — Insert Sample Data

Insert realistic test data so the team can practice queries.

### Step 1 — Insert customers

Add **4 customers**:

| full_name      | email             |
| -------------- | ----------------- |
| Emma Virtanen  | emma@example.com  |
| Jussi Mäkinen  | jussi@example.com |
| Liisa Korhonen | liisa@example.com |
| Olli Nieminen  | _(NULL)_          |

---

### Step 2 — Insert orders

Add **5 orders**. Use the correct `customer_id` values (verify with `SELECT * FROM customers;`).

| customer (full_name) | order_date |
| -------------------- | ---------- |
| Emma Virtanen        | 2024-01-15 |
| Emma Virtanen        | 2024-02-20 |
| Jussi Mäkinen        | 2024-01-22 |
| Liisa Korhonen       | 2024-02-10 |
| Olli Nieminen        | 2024-03-01 |

---

### Step 3 — Insert order items

Add order items so that:

- **Order 1** (Emma, 2024-01-15): 1× Summit 2P Dome Tent (149.99), 2× Ridgeway 30L Daypack (79.95 each)
- **Order 2** (Emma, 2024-02-20): 1× RainShell Waterproof Jacket (119.00)
- **Order 3** (Jussi, 2024-01-22): 1× PolarLite Sleeping Bag -5C (129.00), 1× TrekPro Hiking Poles (54.95)
- **Order 4** (Liisa, 2024-02-10): 3× Thermal Hiking Socks (14.99 each)
- **Order 5** (Olli, 2024-03-01): 1× Headlamp 300 Lumens (24.99), 2× Stainless Steel Water Bottle 1L (19.90 each)

Use the correct `order_id` and `product_id` values. Verify with `SELECT * FROM orders;` and `SELECT * FROM products;` before inserting.

---

### Deliverable

Create `02_seed.sql` with all INSERT statements for customers, orders, and order_items.

---

# Part 4 — JOIN Queries

Write SQL queries that combine data from multiple tables. Refer to [Materials 07](../../Materials/07-SQL-fundamentals-3.md) for JOIN syntax and examples.

The examples below use the **university database** (students, courses, enrollments) from Materials 07. Adapt the same patterns for TrailShop (customers, orders, order_items, products).

### Required queries

1. **Orders with customer names** — List each order’s `order_id`, `order_date`, and the customer’s `full_name`. Use INNER JOIN. Order by `order_date` descending.

2. **Order details with product names** — For each order item, show `order_id`, product `name`, `quantity`, and `unit_price`. Use INNER JOIN between `order_items` and `products`. Order by `order_id`, then product name.

3. **Full order summary** — For each order, show `order_id`, `order_date`, customer `full_name`, product `name`, `quantity`, and `unit_price`. Use JOINs across `orders`, `customers`, `order_items`, and `products`. Order by `order_id`, then product name.

4. **Customers with order count** — List each customer’s `full_name` and the number of orders they have placed. Use LEFT JOIN so that customers with zero orders appear with count 0. Order by order count descending, then by name.

5. **Products never ordered** — List product names that have never been in any order. Use LEFT JOIN from `products` to `order_items` and filter where `order_id` IS NULL.

---

### Deliverable

Create `02_queries.sql` with all 5 queries.

---

# Submission Requirements

Submit these files in the Assignment-2 folder:

- `02_schema.sql` — ALTER TABLE for products, CREATE TABLE for customers, orders, order_items
- `02_seed.sql` — INSERT statements for customers, orders, order_items
- `02_queries.sql` — All 5 JOIN queries

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
├── Exercise-1
├── Exercise-2
└── README.md
```

---

# Self-check

Before submitting, verify:

1. Does `02_schema.sql` run without errors (assuming trailshop database with Assignment-1 tables exists)?
2. Does `02_seed.sql` insert all customers, orders, and order_items without errors?
3. Does query 4 return Olli Nieminen with 1 order (or correct count based on your data)?
4. Does query 5 return products that are not in any order_item?
