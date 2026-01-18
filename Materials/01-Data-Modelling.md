# **0. Introduction — Why Data Modelling Matters**

Before any database is built, we must pause and think.

A database is not merely a container for data — it is a **representation of reality in a structured form**. If that representation is poorly designed, the database becomes confusing, inconsistent, and difficult to use.

**At its core, data modelling answers three fundamental questions:**

- **What exists in the world that we care about?**
    
- **What information do we want to store about these things?**
    
- **How are these things related to one another?**
    

These questions form the foundation of all database design.

### Analogy: Building a House

- You do not begin by laying bricks at random.
    
- First, you sketch a conceptual idea of the house.
    
- Then, you create detailed blueprints.
    
- Finally, you construct the physical building.
    

Similarly, in databases we move through different levels of modelling:

- Conceptual → Logical → Physical
    

This is not extra work — it is essential for creating meaningful, reliable databases.

---


# **1. Three Levels of Data Models**

Modern database design typically distinguishes **three levels of abstraction**. Each serves a different purpose.

[What is data modeling?](https://www.ibm.com/think/topics/data-modeling)

---

## **1.1 Conceptual Data Model — “The Big Picture”**

They are also referred to as domain models and offer a big-picture view of what the system will contain, how it will be organized, and which business rules are involved.

**Purpose:**

- To capture the **main concepts and relationships** in a domain.
    
- To communicate ideas between business stakeholders, analysts, and designers.
    

**Key characteristics:**

- High-level and non-technical
    
- Focuses on meaning rather than structure
    
- Avoids implementation details
    
- Does not specify:
    
    - Primary keys
        
    - Foreign keys
        
    - Data types
        
    - Tables
        

**Example: Conceptual Model for a University**

Main concepts:

- Student
    
- Course
    
- Professor
    
- Department
    

Key relationships:

- Student takes Course
    
- Professor teaches Course
    
- Professor belongs to Department
    

**Takeaway:**

> The conceptual model tells us _what exists and how things relate_, not _how they are stored._

---

## **1.2 Logical Data Model — “The Structured View”**

The logical model introduces structure while remaining independent of any specific database system. Logical data model is less abstract and provide greater detail about the concepts and relationships in the domain under consideration. 

**At this level, we define:**

- Entities
    
- Attributes
    
- Primary keys
    
- Relationships
    
- Cardinality (1:1, 1:N, M:N)
    

This is where **ER diagrams are most commonly used.**

**Example (Logical Model):**

```
Student(student_id, name, email)
Course(course_id, title, credits)

Student >----< Course
```

Here we now:

- Name specific attributes
    
- Identify primary keys
    
- Clearly define relationships
    

**However, we still do NOT specify:**

- SQL syntax
    
- Exact table formats
    
- Indexing strategies
    

**Takeaway:**

> The logical model defines _what the data structure looks like_, but not how it is implemented.

---

## **1.3 Physical Data Model — “The Implementation”**

This is the final stage — where data becomes a real database. Physical data model provide a schema for how the data will be physically stored within a database. As such, they’re the least abstract of all.

At this level, we specify:

- Actual tables
    
- Column data types
    
- Foreign keys
    
- Constraints
    
- Indexes
    

**Example (Physical Model in SQL):**

```sql
CREATE TABLE Student (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE Course (
    course_id INT PRIMARY KEY,
    title VARCHAR(100),
    credits INT
);

CREATE TABLE Enrollment (
    student_id INT,
    course_id INT,
    grade CHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
```

**Takeaway:**

> The physical model is where theory becomes a working database.

---

## **1.4 How the Three Levels Connect**

|Level|Focus|Typical Output|
|---|---|---|
|Conceptual|Meaning of data|Informal diagrams|
|Logical|Structure of data|ER diagrams|
|Physical|Actual storage|SQL tables|

> Each level refines the previous one — adding detail, precision, and technical specificity.

---


# **2. Entities and Attributes**


## **2.1 What is an Entity?**

An **entity** represents a real-world object or concept that:

- Can be uniquely identified
    
- Has meaningful data associated with it
    
- Is relevant to the system
    

**Examples of good entities:**

- Customer
    
- Order
    
- Product
    
- Employee
    
- Bank Account
    

**Poor entity examples:**

- “Today”
    
- “Something”
    
- “Random Event”
    

These are vague, not clearly defined, and not useful for structured storage.

---

## **2.2 Entity Type vs Entity Instance**

It is important to distinguish:

- **Entity Type** → The general category
    
    - Example: Student
        
- **Entity Instance** → A specific real-world object
    
    - Example:
        
        - Student #1001: Alice
            
        - Student #1002: Bob
            

In databases, tables represent **entity types**, while rows represent **entity instances**.

---

## **2.3 What is an Attribute?**

Attributes describe entities. They answer questions like:

- Who is this?
    
- What is this?
    
- When did this happen?
    

**Example: Order Entity**

Possible attributes:

- order_id
    
- order_date
    
- total_amount
    
- shipping_address
    

Each row in an Order table corresponds to one real-world order.

---

## **2.4 Types of Attributes**

### ✅ Simple vs Composite Attributes

- **Simple attribute**: Cannot be divided further
    
    - Example: student_id
        
- **Composite attribute**: Can be broken into parts
    
    - Example: address →
        
        - street
            
        - city
            
        - postal_code
            
        - country
            

Why split composite attributes?

- Easier searching
    
- Better data structure
    
- More flexibility
    

---

### ✅ Single-Valued vs Multi-Valued Attributes

- **Single-valued**: One value per entity
    
    - Example: birth_date
        
- **Multi-valued**: Multiple values per entity
    
    - Example: phone_numbers
        

In relational databases, multi-valued attributes are typically converted into separate tables.

---

### ✅ Derived Attributes

A derived attribute is calculated from other data.

Example:

- Store: date_of_birth
    
- Derive: age
    

This avoids redundancy and inconsistency.

---

## **2.5 Primary Key — The Identifier**

A **primary key** must satisfy:

- Uniqueness — no duplicates
    
- Minimality — contains no unnecessary attributes
    
- Stability — does not change over time
    

Why not use name as a primary key?

- Two people can have the same name
    
- Names can change
    

Hence, we use:

- student_id
    
- employee_id
    
- order_id
    

---


# **3. Relationships**


## **3.1 What is a Relationship?**

A relationship describes how two entities are connected.

Without relationships, a database would be just isolated tables with no meaning.

**Example:**

- Student takes Course
    

This relationship allows us to answer:

- Which students are in which courses?
    

---

## **3.2 Binary vs Ternary Relationships**

Most relationships are **binary** (between two entities).

Example:

- Student — takes — Course
    

Sometimes we have **ternary relationships** involving three entities.

Example:

- Doctor treats Patient in Hospital
    

This is more complex and typically handled in advanced modelling.

---

## **3.3 Relationship Attributes**

Relationships can have their own attributes.

Example:

- Student takes Course
    
    - grade
        
    - semester
        

These are not attributes of Student or Course alone — they belong to the relationship.

---


# **4. Cardinality**


## **4.1 One-to-One (1:1)**

Each instance of one entity relates to at most one instance of another.

Examples:

- Person ↔ Passport
    
- Car ↔ License Plate
    

Often implemented with a **unique foreign key** in one table.

---

## **4.2 One-to-Many (1:N)**

One entity relates to many instances of another.

Examples:

- Department employs many Employees
    
- Customer places many Orders
    

This is the most common relationship in databases.

---

## **4.3 Many-to-Many (M:N)**

Many instances of one entity relate to many of another.

Example:

- Student ↔ Course
    

Cannot be implemented directly — requires a **junction table**.

---


# **5. Optional vs Mandatory Relationships**


## **5.1 Mandatory Participation**

If participation is mandatory, the entity must be part of the relationship.

Example:

- Every Employee must belong to a Department
    

In a database:

- department_id cannot be NULL.
    

---

## **5.2 Optional Participation**

If participation is optional, the entity may or may not participate.

Example:

- A Student may or may not have a Mentor
    

In a database:

- mentor_id can be NULL.
    

---

## **5.3 Combining Cardinality and Optionality**

Example:

- A Department can have many Employees (1:N)
    
- It may have zero employees (optional)
    
- Every Employee must belong to a Department (mandatory)
    

This reasoning is central to good data modelling.

---

# **6. Data modeling process**

Here’s a practical general, **step-by-step process** you can follow and use.

## Step 1: Understand the domain and scope

**Goal:** Know what you are modeling and what you are *not* modeling.

* Read the problem statement and list:

  * What the system is for (purpose)
  * Who uses it (actors/stakeholders)
  * What tasks it must support (use cases)
* Define boundaries:

  * What data must be stored?
  * What’s out of scope?

**Deliverable:** short scope statement + list of use cases (e.g., “enroll student in course”, “record grade”).

---

## Step 2: Collect business rules (requirements as rules)

**Goal:** Turn vague descriptions into clear constraints.

Write rules in natural language:

* “Each order is placed by exactly one customer.”
* “A customer can place many orders.”
* “A course can have many students; a student can take many courses.”
* “An employee may have a parking spot (optional).”

**Deliverable:** numbered list of business rules (this drives your ER diagram correctness).

---

## Step 3: Identify candidate entities (nouns)

**Goal:** Decide the “things” you need to store.

Look for nouns in requirements and ask:

* Is this a *thing* we store data about?
* Does it have multiple instances?
* Does it need a unique identifier?
* Does it have its own attributes?

**Common entities:** Customer, Order, Product, Student, Course, Department.

**Deliverable:** list of candidate entities with a 1-line definition each.

---

## Step 4: Choose identifiers (primary keys) for each entity

**Goal:** Ensure every entity instance can be uniquely identified.

For each entity, pick a key:

* Prefer stable, unique identifiers: `student_id`, `order_id`
* Avoid unstable keys: names, emails (can change)
* If no natural key exists, use a surrogate key (e.g., auto-increment id)

**Deliverable:** entity list updated with **primary keys**.

---

## Step 5: Identify attributes for each entity (properties)

**Goal:** Define what you store about each entity.

For each entity, list attributes and refine:

* Remove attributes that belong to *another* entity
* Break down composite attributes if needed (Address → Street, City, Postcode)
* Mark derived attributes (Age derived from DOB)

**Deliverable:** entity-attribute list (often a “data dictionary” table).

---

## Step 6: Identify relationships (verbs) between entities

**Goal:** Connect entities based on how the domain works.

Look for verbs in requirements:

* Student *enrolls in* Course
* Customer *places* Order
* Department *employs* Employee

For each relationship:

* Give it a clear name (verb phrase)
* Decide which entities it connects

**Deliverable:** relationship list with names and participating entities.

---

## Step 7: Determine cardinality for each relationship (1:1, 1:N, M:N)

**Goal:** Specify “how many” on each side.

Ask two questions per relationship:

1. For one A, how many B can there be?
2. For one B, how many A can there be?

Examples:

* Customer–Order:

  * One Customer → many Orders
  * One Order → one Customer
    ⇒ **1:N**

* Student–Course:

  * One Student → many Courses
  * One Course → many Students
    ⇒ **M:N**

**Deliverable:** relationships annotated with cardinality.

---

## Step 8: Determine optionality (mandatory vs optional participation)

**Goal:** Decide whether participation is required.

Ask:

* “Must every A be related to some B?”
* “Can an A exist without being related to B?”

Examples:

* An Order must have a Customer → **mandatory** on Order side
* A Customer may have zero Orders → **optional** on Customer side
* An Employee must belong to a Department → mandatory
* A Department may have zero Employees → optional

**Deliverable:** each relationship annotated with optional/mandatory on both sides.

---

## Step 9: Handle relationship attributes (and decide if a relationship should become an entity)

**Goal:** Place attributes in the right place.

If a relationship has attributes, it often indicates:

* a many-to-many relationship, or
* a relationship that deserves its own associative entity

Example:

* Student–Course “Enrollment” has: semester, grade
  That pushes you toward an associative entity/table: **Enrollment**.

**Deliverable:** updated model including relationship attributes and associative entities.

---

## Step 10: Draw the conceptual/logical ER diagram

**Goal:** Create a clear ER diagram representation.

Include:

* Entities with primary keys
* Attributes (at least key attributes)
* Relationships with:

  * cardinality
  * optionality

**Checklist for quality:**

* Names are consistent and meaningful
* Every entity has a primary key
* Many-to-many relationships are clearly shown
* Relationship attributes are placed correctly

**Deliverable:** ER diagram (logical model).

---

## Step 11: Validate the model with sample data and queries

**Goal:** Make sure the model supports the required questions.

Create a few example rows (“test cases”) and verify you can answer:

* “Which courses is Student 1001 taking?”
* “How many orders does Customer 5 have?”
* “Which products are in Order 77 and what quantities?”

If you can’t answer a required query, revise:

* entities
* attributes
* relationships
* cardinality/optionality

**Deliverable:** small sample dataset + list of required queries the model supports.

---

## Step 12: Map the ER diagram to relational tables

**Goal:** Convert the logical model into tables.

Use standard mapping rules:

* **Entity → Table**
* **1:N → Foreign key on the N side**
* **M:N → Junction table (composite PK + FKs)**
* **1:1 → FK with UNIQUE (or merge tables if appropriate)**
* **Optional relationship → FK can be NULL**
* **Mandatory relationship → FK is NOT NULL**

**Deliverable:** relational schema (tables, PKs, FKs).

---

## Step 13: Normalize and refine (avoid redundancy)

**Goal:** Remove unnecessary duplication and update anomalies.

Quick checks:

* Does a table have repeating groups or lists? (bad sign)
* Are you storing the same fact in multiple places?
* Can a non-key attribute depend on something other than the whole key?

Typically you aim for **3NF** in basic courses.

**Deliverable:** refined relational schema.

---

## Step 14: Produce the physical model (DB-specific details)

**Goal:** Prepare for implementation in a specific DBMS.

Add:

* Data types (INT, VARCHAR, DATE…)
* Indexes (on PKs, common search columns)
* Constraints (UNIQUE, CHECK, NOT NULL)
* ON DELETE/UPDATE rules as needed

**Deliverable:** SQL DDL script (CREATE TABLE statements).
