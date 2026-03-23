# Self-Check Guide — Recipe / Meal Planner Project

Use this checklist before submitting to verify that your work meets the grading criteria. Tick each item you have completed. Items marked *(required)* are needed for the basic stage.

**Point summary:** Basic 10 pts | Advanced 10 pts | ORM 5 pts | **Total 25 pts**

---

## Basic Stage (10 points)

### ER Diagram (2 pts)

- [ ] *(required)* All entities are shown (categories, recipes, ingredients, and the link tables)
- [ ] Primary keys and foreign keys are indicated
- [ ] Cardinality is clear (1:N, M:N)
- [ ] Optional vs mandatory attributes are shown
- [ ] The diagram is readable (clear labels, no overlapping elements)

### Schema (3 pts)

- [ ] *(required)* All required tables exist
- [ ] Data types are appropriate for each column
- [ ] Constraints are used where needed (NOT NULL, UNIQUE, CHECK)
- [ ] Foreign keys have appropriate referential integrity (what happens on delete)
- [ ] The recipe–category relationship supports multiple categories per recipe
- [ ] `schema.sql` runs without errors on an empty database

### Seed Data (2 pts)

- [ ] *(required)* At least 4 categories
- [ ] At least 6 recipes
- [ ] At least 12 ingredients
- [ ] At least 15 recipe–ingredient links
- [ ] At least 15 recipe–category links
- [ ] At least 2 recipes have multiple categories
- [ ] Each recipe has at least 2 ingredients
- [ ] `seed.sql` runs without errors after the schema

### Queries (3 pts)

- [ ] *(required)* Query 1: Recipes with categories — correct result and ordering
- [ ] Query 2: Ingredients for a recipe — correct result and ordering
- [ ] Query 3: Recipes using a specific ingredient — correct result
- [ ] Query 4: Ingredient count per recipe — correct GROUP BY and COUNT
- [ ] Query 5: Unused ingredients — correct result (ingredients not in any recipe)
- [ ] Query 6: Average prep time by category — correct result, handles empty categories appropriately

---

## Advanced Stage (10 points) — if you completed it

### Extended ER Diagram (1 pt)

- [ ] Users and instructors (or equivalent) are shown
- [ ] Meal plans and their links to users and recipes are shown
- [ ] Primary keys, foreign keys, and cardinality are correct

### Schema Extensions (3 pts)

- [ ] Tables for users and instructors (or roles)
- [ ] Tables for meal plans and plan entries
- [ ] Foreign keys and constraints are correct
- [ ] `schema_advanced.sql` runs without errors on top of the basic schema

### Seed Data Extensions (1 pt)

- [ ] At least 3 users
- [ ] At least 1 instructor
- [ ] At least 2 meal plans
- [ ] Each meal plan has at least 3 recipe entries
- [ ] `seed_advanced.sql` runs without errors

### Indexes (2 pts)

- [ ] Indexes support finding recipes by category
- [ ] Indexes support listing ingredients for a recipe
- [ ] Indexes support finding recipes by ingredient
- [ ] Indexes support searching ingredients by name
- [ ] Indexes support finding meal plans by user
- [ ] Indexes support finding plan entries by recipe

### Roles (2 pts)

- [ ] Instructor role with appropriate privileges
- [ ] Regular user role with appropriate privileges
- [ ] Viewer role (read-only)
- [ ] `roles.sql` runs without errors

### Additional Queries (1 pt)

- [ ] Query 1: Meal plans by user — correct result
- [ ] Query 2: Recipes in a meal plan — correct result with slot information
- [ ] Query 3: Users with meal plan count — includes users with zero plans

---

## Console Application — ORM Stage (5 points) — if you completed it

### Application (5 pts)

- [ ] Application connects to the database using an ORM (not raw SQL)
- [ ] Application lists recipes (with categories)
- [ ] Connection string is in configuration, not hardcoded
- [ ] README explains how to configure, build, and run
- [ ] Application builds and runs successfully

---

## Before Submitting

- [ ] All files are named correctly (see Instructions)
- [ ] No passwords or sensitive data in code or screenshots
- [ ] ER diagram matches your schema
- [ ] You have run the full workflow: schema → seed → queries (and advanced/ORM if applicable)

---

## Estimated Score

| If you completed... | Approx. max points |
|---------------------|--------------------|
| Basic only          | 10                 |
| Basic + Advanced    | 20                 |
| Basic + Advanced + ORM | 25              |

*This guide helps you spot gaps; the instructor uses the full grading matrix for final assessment.*
