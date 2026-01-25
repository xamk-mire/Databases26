# Assignment 1 — TrailShop: Database Setup (Story Requirements)

> [!NOTE]
> Ensure that you have PostgreSQL and pgAdmin installed
> If for some reason you have to use psql (sql shell) study how the psql tool works and is used [psql doc](https://www.postgresql.org/docs/current/app-psql.html)

> [!IMPORTANT]  
> Copy the Assignment-1 folder with the Instructions.md file into your own classroom repository folder (the one you have used for exercise submission)

Before moving in your classroom repository folder structure should look similar to this

```md
your-Classroom-repo-name
├── Assignment-1
│ └── Instructions.md
├── Exercise-1 (optional)
├── Exercise-2 (Submission for ER exercise)
└── README.md
```

## Scenario

You’ve been hired as a junior database developer for a small startup called **TrailShop** — an online store that sells **outdoor gear, hiking equipment, camping essentials, and adventure clothing**.

Before the web developers can start building the store UI, TrailShop needs a working PostgreSQL database with realistic starter data.

This week, your job is to build the first version of the database that stores:

✅ product categories
✅ products inside those categories
✅ enough sample data for the team to test queries

The company wants the database set up in a way that can grow later during the course.

---

# Your Mission

By the end, TrailShop must have:

✅ A local PostgreSQL database called **trailshop**
✅ A table that stores **outdoor product categories**
✅ A table that stores **products** sold by the store
✅ At least 5 categories and 15 products inserted
✅ A few simple queries that confirm the data exists

---

# Part 1 — Create the Database

TrailShop developers want everyone to use the same database name to avoid confusion in future.

📌 Requirement:

- Create a PostgreSQL database called **trailshop**

---

# Part 2 — Build the First Tables

TrailShop wants to group its products into categories (for example: “Tents”, “Hiking Gear”, “Clothing”).

### Category requirements (interpret into columns + rules)

TrailShop needs a way to store categories so that:

- Each category has an **automatically generated numeric identifier**
- Each category has a **name**
- A category name must **always exist**
- Two categories are **not allowed to share the same name**

---

TrailShop also needs to store products and the basic information needed to sell them.

### Product requirements (interpret into columns + rules)

TrailShop products must support the following:

- Each product has an **automatically generated numeric identifier**
- Each product has a **name**, which must always exist
- Each product has a **price**, stored accurately (**money must not be stored as floating-point**)
- Each product has a **stock amount**, stored as a whole number
- Each product must store which category it belongs to by storing the category identifier (**category_id**)

⚠️ Week 1 note:

- Do **not** add foreign key constraints yet
  (relationships + constraints will be added later in the course)

---

### Deliverable file for Part 2

Create a file in:

✅ `01_schema.sql`

This file must contain SQL to create the tables needed for TrailShop.

---

# Part 3 — Insert Sample Data (TrailShop Starter Catalog)

TrailShop wants realistic test data so the development team can immediately start testing product listings and basic queries.

You will insert:

✅ **5 required categories**
✅ **15 required products** (exact names + prices + stock)

---

## Step 1 — Insert the Required Categories

TrailShop’s initial store launch includes these categories (insert them exactly as written):

1. **Tents**
2. **Backpacks**
3. **Sleeping Gear**
4. **Hiking Accessories**
5. **Outdoor Clothing**

📌 Requirements:

- These 5 category names must exist **exactly**
- Category names must be **unique**
- The database must generate the category identifiers automatically

---

## Step 2 — Insert the Required Products

TrailShop wants **15 products** added to the store catalog.

📌 Rules:

- Insert **all products listed below**
- Each product must include:

  - name
  - price
  - stock
  - category_id

- Stock must be a whole number between **0 and 200**
- Prices should be stored accurately (don’t use floating point types)

---

## ✅ Required Products to Insert

### Category: **Tents**

| Product name              |  Price | Stock |
| ------------------------- | -----: | ----: |
| Summit 2P Dome Tent       | 149.99 |    25 |
| TrailLite 1P Tent         | 119.50 |    12 |
| StormGuard 4P Family Tent | 279.00 |     8 |

---

### Category: **Backpacks**

| Product name           |  Price | Stock |
| ---------------------- | -----: | ----: |
| Ridgeway 30L Daypack   |  79.95 |    40 |
| Alpine Trek 55L Pack   | 169.00 |    18 |
| Waterproof Dry Bag 20L |  29.99 |    60 |

---

### Category: **Sleeping Gear**

| Product name                    |  Price | Stock |
| ------------------------------- | -----: | ----: |
| PolarLite Sleeping Bag -5C      | 129.00 |    20 |
| Summer Breeze Sleeping Bag +10C |  89.90 |    35 |
| Ultralight Sleeping Pad         |  49.50 |    50 |

---

### Category: **Hiking Accessories**

| Product name                    | Price | Stock |
| ------------------------------- | ----: | ----: |
| TrekPro Hiking Poles (Pair)     | 54.95 |    30 |
| Headlamp 300 Lumens             | 24.99 |    70 |
| Stainless Steel Water Bottle 1L | 19.90 |    90 |

---

### Category: **Outdoor Clothing**

| Product name                  |  Price | Stock |
| ----------------------------- | -----: | ----: |
| Merino Wool Base Layer Top    |  64.00 |    45 |
| RainShell Waterproof Jacket   | 119.00 |    22 |
| Thermal Hiking Socks (2-Pack) |  14.99 |   120 |

---

## Category Mapping Requirement (Important)

Your products must reference the correct category using `category_id`.

✅ You may assume categories are inserted in the same order as listed:

1. Tents
2. Backpacks
3. Sleeping Gear
4. Hiking Accessories
5. Outdoor Clothing

So your `category_id` values will likely be:

- Tents → `1`
- Backpacks → `2`
- Sleeping Gear → `3`
- Hiking Accessories → `4`
- Outdoor Clothing → `5`

📌 However, your database might assign different IDs depending on how you inserted data.
So you must **verify the IDs** using:

```sql
SELECT * FROM categories;
```

Then use the correct IDs in your product inserts.

---

## Deliverable File

Create:

✅ `01_seed.sql`

It must include:

- Insert statements for the 5 categories
- Insert statements for all 15 products listed above

---

# Part 4 — First Queries for the Team

TrailShop developers want a few simple SQL queries they can run while testing.

Write queries that return:

1. All categories
2. All products
3. Only product names and prices
4. All products that cost more than 50
5. Product names and prices sorted from most expensive → cheapest

### Deliverable file for Part 4

Create a file:

✅ `01_queries.sql`

This file must contain the required queries.

---

# Submission Requirements

Submit these three files inside the assignment repository:

- ✅ `01_schema.sql`
- ✅ `01_seed.sql`
- ✅ `01_queries.sql`

Your classroom repository should look similar to this:

```md
your-Classroom-repo-name
├── Assignment-1
│ ├── 01_schema.sql
│ ├── 01_seed.sql
│ ├── 01_queries.sql
│ └── Instructions.md
├── Exercise-1 (optional)
├── Exercise-2 (Submission for ER exercise)
└── README.md
```
