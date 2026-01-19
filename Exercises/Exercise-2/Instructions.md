# **Exercise 2: ER MODELLING**

# **Design and model: Library Borrowing System**

> **Instructions:**
> Work through each section in order. Write your answers in the blank spaces. 

---

## **PART 0 — Understanding the Problem**

### 📌 Scenario (read carefully)

A small library wants a database to track members borrowing books.

Key requirements:

* The library stores **books** (id, title, publication year).
* Each book has **exactly one publisher**; a publisher can publish many books.
* A book can have **one or more authors**; an author can write many books.
* People register as **members** (id, name, email, join date).
* A member can borrow many books over time.
* A book can be borrowed many times over time, but each borrowing event involves one member and one book.
* For each borrowing, record: **borrow_date, due_date, return_date** (may be empty).
* The library has multiple **branches** (id, name, address).
* Each physical copy of a book belongs to exactly one branch.
* The library can own multiple copies of the same book.

---

## **Data Modelling (Conceptual → Logical)**

### **Step 1 — Identify candidate entities (Noun Hunt)**

Underline nouns in the scenario, then list your candidate entities below:

**Candidate Entities:**

*
*
*
*
*
*
*

---

### **Step 2 — Confirm final entities + 1-line definition**

Choose your final entities and define each in one sentence.

| Entity | One-line definition |
| ------ | ------------------- |
|        |                     |
|        |                     |
|        |                     |
|        |                     |
|        |                     |
|        |                     |
|        |                     |

---

### **Step 3 — Choose Primary Keys (Identifiers)**

For each entity, propose a primary key.

| Entity | Primary Key (PK) |
| ------ | ---------------- |
|        |                  |
|        |                  |
|        |                  |
|        |                  |
|        |                  |
|        |                  |
|        |                  |

> 💬 Reflection: Why are names or titles usually **not** good primary keys?
>
> Your answer:

---

### **Step 4 — Add Essential Attributes**

List key attributes from the requirements (don’t overthink — include only the main ones).

#### (write the name of your entity here)

* PK:
* ## Other attributes:

  *

#### (write the name of your entity here)

* PK:
* ## Other attributes:

  *

#### (write the name of your entity here)

* PK:
* ## Other attributes:

  *
  *

#### (write the name of your entity here)

* PK:
* ## Other attributes:

#### (write the name of your entity here)

* PK:
* ## Other attributes:

#### (write the name of your entity here)

* PK:
* ## Other attributes:

  *

#### (write the name of your entity here)

* PK:
* ## Other attributes:

  *
  *

---

### **Step 5 — Identify Relationships (Verb Hunt)**

Write relationships in the form: **Entity — verb — Entity**

*
*
*
*
*

---

### **Step 6 — Determine Cardinality (1:1, 1:N, M:N)**

Fill in the table below.

| Relationship | Cardinality | Reason (short) |
| ------------ | ----------- | -------------- |
|              |             |                |
|              |             |                |
|              |             |                |
|              |             |                |
|              |             |                |

---

### **Step 7 — Determine Optional vs Mandatory Participation**

Answer the following questions:

(you can use ':heavy

1. **Must every Book have a Publisher?**

   * [] Yes (Mandatory) [] No (Optional)
   * Why?

2. **Can a Publisher exist with zero Books?**

   * [] Yes [] No
   * Why?

3. **Must every Book have at least one Author?**

   * [] Yes [] No
   * Why?

4. **Must every Copy belong to a Branch?**

   * [] Yes [] No
   * Why?

5. **Is return_date in Borrowing mandatory or optional?**

   * [] Mandatory [] Optional
   * Why?



## Draw Your ER Diagram (Logical Model)**

### **Step 8 — Draw Entities (boxes)**

Draw a rectangle for each entity and write its **primary key** clearly.

Use this space (or a separate sheet):

- You can draw the ER diagram using software or app
- Once you have finished drawing the diagram, you can download or just take a screenshot of the diagram
- Add the image inside your exercise folder/repository
- You should now be able to add the image as a link here [Adding images in markdown](https://www.markdownguide.org/basic-syntax/#images-1)

```
[ Add your ER diagram here ]
```

---

### **Step 9 — Add Relationships**

Add labeled lines between entities -> explain the relationships between entities

---

### **Step 10 — Mark Cardinality & Optionality**

On each relationship, clearly mark:

* 1, N, or M
* Mandatory vs Optional (if your notation supports it)

---

## **Self-Check (Validation Questions)**

Can your model support the following?

Mark ✔ or ✘ and briefly explain.

1. Can a member borrow multiple books over time?

   * [] Yes [] No
   * Why?

2. Can the same copy be borrowed multiple times in different months?

   * [] Yes [] No
   * Why?

3. Can a book have multiple authors?

   * [] Yes [] No
   * Why?

4. Can a book exist without a publisher?

   * [] Yes [] No
   * Why?

5. Can a borrowing have no return_date?

   * [] Yes [] No
   * Why?

---
