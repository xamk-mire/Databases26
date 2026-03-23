# Project — Recipe / Meal Planner Database

## Introduction

This project gives you the opportunity to design and implement a PostgreSQL database from scratch. You will work through a realistic scenario: a cooking school and meal-planning service needs a database to store recipes, ingredients, and categories. As the project progresses, you may extend it with users, instructors, meal plans, and a console application that connects to the database via an ORM.

You will make your own design decisions—choosing entities, relationships, constraints, and implementation details—while satisfying the business requirements. The project is structured in stages: a mandatory basic stage, followed by optional advanced and ORM stages. Each stage builds on the previous one and contributes to your total score.

---

> [!NOTE]
> This is a **student-designed project** in multiple stages. You interpret the requirements, design the schema, and implement the database. Use the course materials to make correct design decisions.

> [!IMPORTANT]
> Complete Assignments 1–4 before starting the basic stage. The advanced stage builds on the basic stage. The ORM stage builds on advanced.

---

## Overview

| Stage        | Focus                                                         | Prerequisites                             | Grading                               |
| ------------ | ------------------------------------------------------------- | ----------------------------------------- | ------------------------------------- |
| **Basic**    | Recipes, categories, ingredients, and recipe–ingredient links | Assignments 1–3                           | **Mandatory** — 10 points             |
| **Advanced** | Users, instructors, meal plans/menus, indexes, roles          | Basic stage completed                     | **Optional** — 10 points if completed |
| **ORM**      | Console application with ORM                                  | Basic (and optionally advanced) completed | **Optional** — 5 points if completed  |

The basic stage is mandatory (10 points). The advanced stage is optional (10 points). The ORM stage is optional (5 points). **Total: 25 points.** Completing all three stages earns the full 25 points.

For how to present your project with screenshots and explain your design choices, see [Reporting-Guide.md](Reporting-Guide.md). Before submitting, use [Self-Check-Guide.md](Self-Check-Guide.md) to verify your work.

---

## Scenario

A local cooking school and meal-planning service wants a PostgreSQL database. The system manages **recipes**, **ingredients**, and **categories**. Later, it will support **users** who browse and plan meals, **instructors** who create and edit recipes, and **meal plans** (menus) for organising recipes over time.

---

# Stage 1 — Basic

Design and implement the core recipe database.

---

## Basic — Business Requirements

### Categories

- The system stores recipe categories (e.g. Breakfast, Dessert, Main Course, Soup).
- Each category has a unique identifier and a name.
- Category names must be unique. No two categories may share the same name.

### Recipes

- Each recipe has a name and may have instructions (which can be long).
- Recipes may store prep time (in minutes) and number of servings.
- A recipe can belong to one or more categories. A recipe must have at least one category at all times.
- Prep time, if provided, must be non‑negative.
- Servings, if provided, must be at least 1.

### Recipe–Category relationship

- A recipe can belong to one or more categories. A category can contain many recipes.
- For each recipe–category pair, the system stores the association.
- Deleting a recipe must remove its category associations.
- Deleting a category must remove its associations to recipes. Your design must ensure that no recipe is left without at least one category (e.g. by preventing deletion of a category that would leave a recipe with none).

### Ingredients

- Ingredients are reusable across recipes (e.g. flour, milk, olive oil).
- Each ingredient has a unique identifier and a unique name.
- Ingredients may have a typical default unit (e.g. g, ml, pcs).

### Recipe–Ingredient relationship

- A recipe uses one or more ingredients. An ingredient may appear in many recipes.
- For each recipe–ingredient pair, the system must store the quantity and the unit (e.g. 200 g flour, 2 eggs).
- Quantity must be positive.
- Deleting a recipe must remove its ingredient associations.
- An ingredient that appears in any recipe must not be deletable until it is no longer referenced.

---

## Basic — Part 1: ER Diagram

Produce an ER diagram that:

- Shows all entities needed to meet the basic business requirements
- Shows primary keys, foreign keys, and cardinality
- Shows optionality (mandatory vs optional attributes/relationships)

Use draw.io, dbdiagram.io, or similar. Export as PNG or PDF.

**Deliverable:** `er_diagram.png` or `er_diagram.pdf`

---

## Basic — Part 2: Schema

Implement the PostgreSQL schema so that it satisfies all basic business requirements. Use appropriate data types, constraints, and referential integrity rules.

**Deliverable:** `schema.sql` — all statements needed to create the tables

---

## Basic — Part 3: Seed Data

Insert realistic test data so that:

- There are at least 4 categories
- There are at least 6 recipes
- There are at least 12 ingredients
- There are at least 15 recipe–ingredient associations
- There are at least 15 recipe–category associations (each recipe has at least 1 category; at least 2 recipes have multiple categories)
- Each recipe has at least 2 ingredients

**Deliverable:** `seed.sql` — all `INSERT` statements

---

## Basic — Part 4: Queries

Write SQL queries that produce the following results. Choose appropriate techniques based on the course materials.

1. **Recipes with categories** — List all recipes with their category name(s). A recipe with multiple categories may appear once per category. Order by category name, then recipe name.

2. **Ingredients for a recipe** — For a chosen recipe (e.g. by name), show ingredient name, quantity, and unit, ordered by ingredient name.

3. **Recipes using an ingredient** — List all recipes that use a chosen ingredient (e.g. flour), showing recipe name and category (or categories).

4. **Ingredient count per recipe** — For each recipe, show recipe name and the number of ingredients it uses, ordered by ingredient count descending.

5. **Unused ingredients** — List ingredients that do not appear in any recipe.

6. **Average prep time by category** — For each category, show category name and the average prep time (in minutes) of its recipes, ordered by average prep time descending. A recipe in multiple categories contributes to each category’s average. Categories with no recipes or no prep times need appropriate handling.

**Deliverable:** `queries.sql` — all 6 queries with brief comments

---

# Stage 2 — Advanced

Extend the database with users, instructors, meal plans, indexes, and roles. The advanced stage assumes the basic stage is complete and working.

---

## Advanced — Business Requirements

### Users

- The system stores users (people who browse recipes and create meal plans).
- Each user has a unique identifier.
- Users must be identifiable (e.g. by name or email) in a way that prevents duplicates where appropriate.

### Instructors

- Instructors are users who can create and edit recipes, ingredients, and categories.
- The system must distinguish instructors from regular users.
- Regular users can browse recipes and create personal meal plans but cannot modify recipes, ingredients, or categories.

### Meal plans (menus)

- A meal plan is a named collection of recipes organised for a period or for specific meals (e.g. a weekly menu, or Monday lunch, Tuesday dinner).
- A meal plan belongs to a user.
- A meal plan contains one or more recipe references. The system must record which recipe is planned for which slot (e.g. day, meal type, or order).
- Deleting a user may remove their meal plans, or prevent deletion if they have plans—your design must handle this consistently.
- Deleting a recipe must be prevented if it is referenced in any meal plan, or your design must define how such references are updated or removed.

### Indexes

- Add indexes to support:
  - Finding recipes by category
  - Listing ingredients for a given recipe
  - Finding recipes that use a given ingredient
  - Searching ingredients by name
  - Finding meal plans by user
  - Finding meal plan entries by recipe

### Roles

- Define database roles so that:
  - **Instructors** can read, insert, and update recipes, recipe–ingredient links, recipe–category links, ingredients, and categories. They may also need appropriate access to user-related tables depending on your design.
  - **Regular users** can read recipes, ingredients, and categories, and can manage their own meal plans (read, insert, update, delete their own data).
  - **Viewers** can only read all tables (e.g. for reporting or auditing).

---

## Advanced — Part 1: Extended ER Diagram

Update your ER diagram to include:

- Users and instructors
- Meal plans and their relationship to users and recipes
- All new primary keys, foreign keys, and cardinality

**Deliverable:** `er_diagram_advanced.png` or `er_diagram_advanced.pdf` (or an updated version of your basic diagram)

---

## Advanced — Part 2: Schema Extensions

Add or alter tables to support users, instructors, and meal plans. Ensure referential integrity and constraints match the advanced business requirements.

**Deliverable:** `schema_advanced.sql` — all `CREATE TABLE`, `ALTER TABLE`, and related statements for the extensions

---

## Advanced — Part 3: Seed Data Extensions

Add seed data so that:

- There are at least 3 users, including at least 1 instructor
- There are at least 2 meal plans
- Each meal plan has at least 3 recipe entries

**Deliverable:** `seed_advanced.sql` — all `INSERT` statements for the new data

---

## Advanced — Part 4: Indexes

Add indexes to support the use cases listed in the advanced business requirements.

**Deliverable:** `indexes.sql` — `CREATE INDEX` statements

---

## Advanced — Part 5: Roles

Define roles and grant appropriate privileges as specified in the advanced business requirements.

**Deliverable:** `roles.sql` — `CREATE ROLE`, `CREATE USER`, and `GRANT` statements

---

## Advanced — Part 6: Additional Queries

Write SQL queries that produce the following results:

1. **Meal plans by user** — List all meal plans with their owner (user name or identifier), ordered by owner, then meal plan name.

2. **Recipes in a meal plan** — For a chosen meal plan, show recipe name, category (or categories), and the slot (day/meal/order) it is assigned to, ordered appropriately.

3. **Users with meal plan count** — For each user, show user identifier/name and the number of meal plans they have, ordered by meal plan count descending. Include users with zero meal plans.

**Deliverable:** `queries_advanced.sql` — all 3 queries with brief comments

---

# Stage 3 — ORM Console Application (Optional)

Build a simple console application that connects to your Recipe / Meal Planner database using an ORM. This stage is done **after** the advanced stage (or after the basic stage if you did not complete advanced).

---

## Technology

- **Default:** .NET 10 with Entity Framework Core
- **Alternative:** You may use another language and ORM (e.g. Python with SQLAlchemy, Java with Hibernate, Node.js with Prisma) if you prefer. The application must connect to PostgreSQL and use an ORM—not raw SQL strings.

---

## ORM Stage — Requirements

### Application behaviour

- The application connects to your Recipe / Meal Planner database (basic schema, or basic + advanced if completed).
- The application uses an ORM to read data. At minimum, it must list recipes (with their categories) from the database.
- Optionally, the application may support adding, updating, or deleting data (e.g. new recipes, meal plan entries).
- The application must not hardcode connection strings or secrets in source code. Use configuration (e.g. `appsettings.json`, environment variables, or User Secrets for .NET).

### Deliverables

1. **Source code** — The full console application project (e.g. `RecipePlannerConsole/` or equivalent).
2. **README** — A short README in or next to the project that explains:
   - How to configure the connection string
   - How to build and run the application
   - Which technology and ORM you used (if not .NET + EF Core)

### For .NET + EF Core

- Use .NET 10 and EF Core with the PostgreSQL provider.
- You may scaffold the DbContext and entities from your existing database, or define them manually and use migrations. The application must connect to the database you built in stages 1 and 2.
- See [Materials 13 — Entity Framework Core](../../Materials/13-Entity-Framework-Core.md), [Materials 16 — EF Core Scaffolding](../../Materials/16-Entity-Framework-Core-Scaffolding.md), and [Materials 15 — EF Core Migrations](../../Materials/15-Entity-Framework-Core-Migrations.md) for guidance.

---

**Deliverable:** Project folder (e.g. `RecipePlannerConsole/`) and `README.md` with setup and run instructions.

---

# Submission Checklist

### Basic stage (mandatory — required for project points)

| File                  | Stage | Required |
| --------------------- | ----- | -------- |
| er_diagram.png / .pdf | Basic | Yes      |
| schema.sql            | Basic | Yes      |
| seed.sql              | Basic | Yes      |
| queries.sql           | Basic | Yes      |

### Advanced stage (optional — additional points)

| File                           | Stage    | Required               |
| ------------------------------ | -------- | ---------------------- |
| er_diagram_advanced.png / .pdf | Advanced | If completing advanced |
| schema_advanced.sql            | Advanced | If completing advanced |
| seed_advanced.sql              | Advanced | If completing advanced |
| indexes.sql                    | Advanced | If completing advanced |
| roles.sql                      | Advanced | If completing advanced |
| queries_advanced.sql           | Advanced | If completing advanced |

### ORM stage (optional — 5 points)

| Deliverable                                      | Stage | Required                |
| ------------------------------------------------ | ----- | ----------------------- |
| Console app project (e.g. RecipePlannerConsole/) | ORM   | If completing ORM stage |
| README with setup/run instructions               | ORM   | If completing ORM stage |

### Report (mandatory)

| Deliverable             | Required                                                   |
| ----------------------- | ---------------------------------------------------------- |
| REPORT.md or REPORT.pdf | Recommended — use [Reporting-Guide.md](Reporting-Guide.md) |

**Grading:** Basic = 10 pts (mandatory), Advanced = 10 pts (optional), ORM = 5 pts (optional). **Total: 25 points.**

Use [Self-Check-Guide.md](Self-Check-Guide.md) to verify your work before submitting.

### Folder structure

```
Project-Recipe-MealPlanner/
├── Instructions.md (this file)
├── Reporting-Guide.md
├── Self-Check-Guide.md
├── er_diagram.png
├── schema.sql
├── seed.sql
├── queries.sql
├── er_diagram_advanced.png
├── schema_advanced.sql
├── seed_advanced.sql
├── indexes.sql
├── roles.sql
├── queries_advanced.sql
├── RecipePlannerConsole/     (optional — if completing ORM stage)
│   └── (project files)
├── README.md                 (for ORM stage setup/run instructions)
└── REPORT.md or REPORT.pdf   (recommended — see Reporting-Guide.md)
```

---

# Self-Check

### Basic stage

1. Does the schema run without errors on an empty database?
2. Does the seed data run without errors after the schema?
3. Do all 6 queries return correct results for your data?
4. Is the ER diagram consistent with your schema?
5. Do constraints and referential integrity rules match the business requirements?

### Advanced stage

1. Does `schema_advanced.sql` run without errors on top of the basic schema?
2. Does `seed_advanced.sql` run without errors?
3. Do all advanced queries return correct results?
4. Do the indexes support the intended use cases?
5. Do the roles have the correct privileges?

### ORM stage

1. Does the application connect to the database using an ORM (not raw SQL)?
2. Does it list recipes (and their categories) from the database?
3. Is the connection string configured via configuration (not hardcoded)?
4. Does the README explain how to build, configure, and run the application?

---

# References

- Materials 1-16
- [Reporting-Guide.md](Reporting-Guide.md) — How to present the project with screenshots and design reasoning
