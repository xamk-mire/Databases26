
# 1) What is a Relational Database?

[IBM: What is a relational dabase?](https://www.ibm.com/think/topics/relational-databases#228874317)

A relational database is a way of organizing information so it feels less like a chaotic pile of notes and more like a well-ordered library.  
Instead of storing “everything everywhere,” a relational database stores data in **tables** that can be **linked** together through carefully chosen rules.

At its core, it’s built on the **relational model**, introduced by **E. F. Codd**, which treats data as a set of relations (tables) and uses logic-based operations to manipulate them.

### The key idea

The relational database asks:

> “What are the _things_ in our world, what are their _properties_, and how are they _connected_?”

 In a school system:

- Things: **Students**, **Courses**, **Teachers**
    
- Properties: student name, course title, etc.
    
- Connections: students enroll in courses, teachers teach courses
    

---

# 2) The Relational Model

A database can store data in many ways.  
But the relational database makes a very specific promise:

> Data will not be stored as a messy collection of facts,  
> but as a system of **structured relations** that can be reasoned about.

The **relational model** is the idea behind this promise.  
It is the _theory_ that explains why relational databases behave like they do—why tables exist, why keys matter, and why SQL can combine data from many places without losing meaning.

Importantly:

- the relational model is **not PostgreSQL**
    
- it is **not MySQL**
    
- it is **not a software product**
    

It is the _design philosophy_ and mathematical framework that those systems implement.

When you learn the relational model, you are learning what makes a relational database **reliable, consistent, and predictable**.

##  Core Concepts (Keywords + Meaning)

The relational model is built from a small set of powerful building blocks.  
Each one is simple—but together they allow databases to represent complex worlds.

***
### **Relation** → a table

A **relation** is a collection of structured facts about a certain kind of thing.

✅ Key points:

- a relation is _like_ a table in modern databases
    
- it has a **name** (e.g., `Students`)
    
- it consists of **attributes** (columns)
    
- it contains **tuples** (rows)
    

Example relation: `Students`

|StudentID|Name|Email|
|---|---|---|
|1|Aino|aino@uni.fi|
|2|Mika|mika@uni.fi|

In the “pure” mathematical relational model, relations are treated as **sets**, meaning:

- duplicates do not exist (a set cannot contain the same element twice)
    
- ordering does not matter
    

Real databases may _appear_ to allow duplicates, but **keys and constraints** are how we bring the system back into discipline.

***
### **Tuple** → a row

A **tuple** is one complete record in a relation.

✅ Key points:

- each tuple represents **one entity instance**
    
- a tuple contains one value for each attribute
    
- tuple order does not matter in theory
    

Example tuple:

- `(StudentID=1, Name="Aino", Email="aino@uni.fi")`
    

A tuple is like a single “card” in the library catalogue.  
It is a complete description of one object—using the structure defined by the relation.

***
### **Attribute** → a column

An **attribute** is a named property describing something in the relation.

✅ Key points:

- attributes define the _meaning_ of values in a tuple
    
- they have names (e.g., `Email`)
    
- they have data types/domains (text, integer, date…)
    

Example attributes in `Students`:

- `StudentID` → identity number
    
- `Name` → student name
    
- `Email` → contact information
    

🟦 A helpful way to explain attributes:

> If a tuple is a **sentence**, attributes are the **grammar rules** that give it structure.

***
### **Domain** → allowed values for an attribute

A **domain** is the set of values an attribute is allowed to take.

✅ Key points:

- domains prevent invalid values
    
- domains express meaning (“what kinds of things belong here?”)
    
- in practice, domains are enforced using:
    
    - **data types**
        
    - **constraints** (NOT NULL, CHECK, etc.)
        

Examples:

- `StudentID` domain might be: positive integers
    
    - `{1, 2, 3, 4, …}`
        
- `Credits` domain might be: integers from 1 to 20
    
    - `{1, 2, …, 20}`
        
- `Email` domain might be: strings that match email rules
    
    - enforced by uniqueness and formatting rules (often via application or constraint checks)
        

Example in SQL (PostgreSQL):

```sql
Credits INTEGER CHECK (Credits BETWEEN 1 AND 20)
```
`

Domains are how we stop the database from accepting nonsense like:

- credits = -500
    
- student_id = "banana"

***
### **Instance** → the current contents (data right now)

If schema is the blueprint, an **instance** is the current population of data.

✅ Key points:

- schema is stable (changes rarely)
    
- instance changes constantly (rows inserted/updated/deleted)
    
- the same schema can have many different instances over time
    

Example:

- Monday morning: 10 students exist in the table
    
- Friday afternoon: 200 students exist
    

The **table structure** remains the same, but the **instance** has grown.

---

# 3) Tables, Rows, Columns (Relation, Tuple, Attribute)

## A) Tables (Relations)

A table is a collection of data about one type of thing.

🔑 Important points:

- A table has a **name**
    
- A table has **columns** (attributes)
    
- A table contains **rows** (tuples)
    
- Each row is one “record” describing a single object
    

Example table: `Students`

|StudentID|Name|Email|
|--:|---|---|
|1|Aino|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika|[mika@uni.fi](mailto:mika@uni.fi)|

**What does this table represent?**

- The **concept** “Student”
    
- Each row represents **one student**
    
- Each column represents **a property of a student**
    

---

## B) Columns (Attributes)

A column defines a property shared by all rows.

✅ Key points:

- Each column has a **name** (`Name`, `Email`)
    
- Each column has a **data type**
    
    - e.g. integer, text, date
        
- Each column has a **domain**
    
    - e.g. `StudentID` must be whole numbers ≥ 1
        
    - `Email` should follow an email format (rule often enforced via constraints)
        

A well-designed column is:

- **Atomic** (single value, not a list)
    
- **Consistent** (same meaning in every row)
    

⚠️ Bad column design example  
Storing multiple values in one column:

|StudentID|Name|PhoneNumbers|
|--:|---|---|
|1|Aino|0501..., 0442...|

Better approach:

- create a separate `StudentPhones` table instead
    

---

## C) Rows (Tuples)

A row is one complete instance of the entity in the table.

✅ Key points:

- Each row is a single record
    
- Every row should be uniquely identifiable
    
- Rows don’t rely on “position” (row #17 has no meaning on its own)
    

Example row:

- `(StudentID=1, Name="Aino", Email="aino@uni.fi")`
    

---

# 4) Keys: The Identity of Data

In relational databases, identity matters.  
A database must be able to distinguish one row from every other row—reliably, always.

This is where **keys** come in.

---

## A) Primary Key (PK)

A primary key is the **main identifier** for rows in a table.

✅ Primary key rules:

- **Unique**: no duplicates allowed
    
- **Not NULL**: must always exist
    
- **Stable**: should not change frequently
    
- **Minimal**: should contain no unnecessary attributes
    

Example: `Students(StudentID)` as primary key.

### Why not use names as primary keys?

Because names are not stable or unique.

Two students might both be named “Mika.”  
One Mika might later change their name.

So instead we use:

- `StudentID` (a generated integer)
    
- or a UUID (globally unique identifier)
    

---

## B) Candidate Keys

A candidate key is any column (or group of columns) that _could_ uniquely identify rows.

Example: If student emails must be unique:

- `StudentID` = candidate key ✅
    
- `Email` = candidate key ✅
    

Primary key is the one we officially choose.

---

## C) Composite Keys

Sometimes uniqueness requires multiple columns.

Example: Enrollment records:

|StudentID|CourseID|Grade|
|--:|--:|---|
|1|101|5|
|1|102|4|

A student can take many courses.  
A course can contain many students.

Neither `StudentID` alone nor `CourseID` alone uniquely identifies a row.  
But together:

✅ Composite key: `(StudentID, CourseID)`

Composite keys are typically used in junction tables by combining two or more Foreign keys. This removes the need of creating additional column/attribute to store identifier, and thus decreases the complexity and potentially even prevents invalid data errors. 

---

# 5) Foreign Keys: The Threads Between Tables

A foreign key (FK) is how tables “know each other.”

It’s a column in one table that references the primary key in another table.

### Why foreign keys matter

They enforce **referential integrity**, meaning:

> “You cannot reference something that does not exist.”

---

## Example: Students and Courses

### `Students`

|StudentID (PK)|Name|
|--:|---|
|1|Aino|
|2|Mika|

### `Courses`

|CourseID (PK)|Title|
|--:|---|
|101|Databases|
|102|Web Development|

### `Enrollments`

|StudentID (FK)|CourseID (FK)|
|--:|--:|
|1|101|
|1|102|
|2|101|

🔎 What’s happening?

- `Enrollments.StudentID` references `Students.StudentID`
    
- `Enrollments.CourseID` references `Courses.CourseID`
    

✅ This enables queries like:

- “Which courses is Aino enrolled in?”
    
- “Which students are taking Databases?”
    

---

## Foreign Key rules (important bullets)

- A foreign key value must either:
    
    - match an existing primary key value, or
        
    - be NULL (if allowed)
        
- Foreign keys help prevent “orphaned records”
    

### Orphan example (not allowed)

If a student is deleted but enrollments remain:

|StudentID|CourseID|
|--:|--:|
|999|101|

Student 999 does not exist → the database should reject it.

---

# 6) Relationships Between Tables (quick recap from Data Modelling)

Relational databases shine when modeling real-world relationships.

## A) One-to-One (1:1)

Each row in A relates to at most one row in B.

Example:

- A person has exactly one passport (in some simplified models)
    

Often implemented by:

- sharing the same primary key in both tables, or
    
- a unique foreign key
    

---

## B) One-to-Many (1:N)

One row in A relates to many rows in B.

Example:

- One teacher teaches many courses
    
- One customer makes many orders
    

Implementation:

- foreign key on the “many” side
    

`Orders(CustomerID FK → Customers.CustomerID)`

---

## C) Many-to-Many (M:N)

Many rows in A relate to many rows in B.

Example:

- Students take many courses
    
- Courses contain many students
    

Implementation:

- you need a **junction table** (also called a bridge table)
    

`Enrollments(StudentID FK, CourseID FK)`

This is extremely common.

---

# 7) Constraints: The Database as a Rulebook

Constraints are rules that keep data clean and meaningful.

### Common constraints

- **PRIMARY KEY**
    
    - uniqueness + not null
        
- **FOREIGN KEY**
    
    - references another table
        
- **NOT NULL**
    
    - must contain a value
        
- **UNIQUE**
    
    - cannot repeat
        
- **CHECK**
    
    - must satisfy a condition (e.g., grade between 0 and 5)
        
- **DEFAULT**
    
    - provides a default value if none is given
        

---

## Example constraint reasoning

If course credits must be between 1 and 20:

- **CHECK (Credits BETWEEN 1 AND 20)**
    

This prevents accidental bad values like `-100` or `9999`.

---

# 8) A Full Mini-Database Example 

Below we have a example of a mini database

### Table 1: Student

| StudentID (PK) | Name |
| -------------: | ---- |
|              1 | Aino |
|              2 | Mika |

### Table 2: Course

| CourseID (PK) | Title      |
| ------------: | ---------- |
|           101 | Databases  |
|           102 | Algorithms |

### Table 3: Enrollment (junction)

| StudentID (FK) | CourseID (FK) |
| -------------: | ------------: |
|              1 |           101 |
|              1 |           102 |
|              2 |           101 |

### Questions we can answer now

✅ “Which courses is Aino taking?”

- Find Aino’s StudentID = 1
    
- Look up enrollments where StudentID = 1 → CourseIDs 101 & 102
    
- Join with Courses to get course titles
    

> In this example we don't have to know the CourseID's in the Course table. Just by knowing the Id of the student we are able to retrieve the relevant data from the Course table because of the Enrollment table. 

✅ “How many students are taking Databases?”

- CourseID for Databases = 101
    
- Count enrollments where CourseID = 101 → 2 students
    

This is the relational model in action:

- tables hold structure
    
- keys build connections
    
- queries bring meaning
    

---

# 9) Why Relational Databases Are Powerful

Relational databases are loved because they combine:

- **clarity** (data structure is explicit)
    
- **correctness** (constraints prevent nonsense)
    
- **queryability** (SQL is expressive)
    
- **scalability** (handles large datasets efficiently)
    

They work well when:

- relationships matter
    
- data must be reliable
    
- updates must remain consistent
    
- you care about correctness over “quick storage”
    

---

# 10) Common Beginner Mistakes 

Every beginner builds their first database the same way a beginner builds their first city in a simulation game:

- everything is placed too close together,
    
- roads are missing,
    
- and the moment growth begins, the design starts to fight itself.
    

The good news is that these mistakes are not signs of failure.  
They are _proof that the developer is finally thinking in data_.

A relational database is not merely a place to store information -> 
it is a system designed to protect information from becoming inconsistent, duplicated, and contradictory.

These mistakes are the natural first steps on that path.

---

## Mistake 1: Mixing multiple concepts into one table

### (One table to rule them all)

A common beginner instinct is to create a single “mega-table” that contains everything they can think of.

They want one place where all information is visible at once — like a spreadsheet.

### What it looks like (example)

A table called `StudentsAndCourses`:

|StudentID|StudentName|CourseID|CourseTitle|Credits|
|--:|---|--:|---|--:|
|1|Aino|101|Databases|5|
|1|Aino|102|Algorithms|6|
|2|Mika|101|Databases|5|

At first glance, it seems fine:

- it shows students
    
- it shows courses
    
- it shows enrollments
    

But the table is quietly doing something dangerous:

✅ It is repeating the same facts over and over.

---

### Why this is a problem

The table contains _three different concepts_ blended into one:

- **Student** information
    
- **Course** information
    
- **Enrollment** (the relationship between them)
    

This creates several issues:

#### 1) **Duplication**

- The student name `"Aino"` is repeated in every row where Aino appears.
    
- The course title `"Databases"` is repeated in every row where Databases appears.
    

Duplication is not just wasteful. It is risky.

#### 2) **Update anomalies** (the “two truths” problem)

What happens if the course title changes?

Suppose `"Databases"` becomes `"Database Systems"`.

Now you must update multiple rows:

- Row 1: update course title
    
- Row 3: update course title
    
- And if you miss one row?
    

You end up with a database that says **two different truths at once**.

#### 3) **Insertion anomalies**

What if you want to add a new course that no student has enrolled in yet?

In the mega-table, you cannot insert a course without also inserting a student relationship row.

So the table forces you to invent meaningless data just to satisfy the structure.

#### 4) **Deletion anomalies**

If you delete the last student enrolled in a course, you might accidentally delete the only place where the course information existed.

In other words:

> Removing one relationship could erase an entire concept.

---

### Fix: separate the concepts into separate tables

A relational database works best when each table represents **one concept**.

✅ Correct approach:

- `Students` → who the student is
    
- `Courses` → what the course is
    
- `Enrollments` → who is enrolled in what
    

**Students**

|StudentID|Name|
|--:|---|
|1|Aino|
|2|Mika|

**Courses**

|CourseID|Title|Credits|
|--:|---|--:|
|101|Databases|5|
|102|Algorithms|6|

**Enrollments**

|StudentID|CourseID|
|--:|--:|
|1|101|
|1|102|
|2|101|

✅ Benefits:

- student facts are stored once
    
- course facts are stored once
    
- enrollment is stored cleanly as a connection
    

A good relational design is like a good story:

- characters have their own identity
    
- locations have their own identity
    
- relationships connect them without rewriting them again and again
    

---

---

## Mistake 2: Using real-world values as primary keys

### (The temptation of “meaningful identifiers”)

Beginners often choose a primary key that _looks meaningful_:

- email addresses
    
- phone numbers
    
- national ID numbers
    
- usernames
    

Because it feels natural:

> “This is unique in real life, so it should be unique in the database.”

### Example (risky design)

```sql
CREATE TABLE students (
  email VARCHAR(255) PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL
);
```

This seems convenient:

- no separate ID needed
    
- emails are unique (usually)
    

But this is a fragile foundation.

---

### Why this is risky

#### 1) **Real-world values can change**

People change emails. Often.

- change of provider (gmail → outlook)
    
- name change (aino.laine → aino.virtanen)
    
- privacy reasons
    
- work/school changes
    

If the email is the primary key, changing it becomes hard.

In fact, changing a primary key can become dangerous because:

✅ other tables may reference it  
✅ foreign keys depend on it

When identity changes, everything connected to it must change too.

---

#### 2) **A person might have multiple values**

A student might have:

- one university email
    
- one personal email
    

Which one should be the primary key?

Real-world identifiers are not always as stable and singular as they appear.

---

#### 3) **Real-world values carry meaning (and meaning causes trouble)**

Primary keys should ideally be **meaningless** identifiers.

Because meaningful identifiers create accidental logic:

- does the email tell something about the organization?
    
- will it be reused?
    
- will it be considered personal data?
    

Using meaningful identifiers as primary keys mixes identity with “business meaning.”

---

### Fix: Use a stable, generated key

Instead of using email as the primary key:

✅ use an auto-generated integer or UUID  
✅ store email as a normal attribute  
✅ enforce uniqueness separately if needed

**PostgreSQL example (recommended):**

```sql
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);
```

Now:

- `student_id` identifies the student forever
    
- email can change without breaking relationships
    
- uniqueness is still enforced
    

Primary keys should behave like a fingerprint inside the system:

> internal, stable, and never meant to be “human-friendly.”

---

---

## Mistake 3: Storing repeating values in one column

### (The “list inside a cell” problem)

Beginners often try to compress multiple values into a single column by storing a list:

Example:

|StudentID|Name|Courses|
|--:|---|---|
|1|Aino|"Math, Physics, Databases"|
|2|Mika|"Databases"|

This looks like it saves time.

But it quietly breaks one of the central ideas of relational databases:

✅ **Each cell should contain one value.**  
This is known as **atomicity** and is part of good relational design.

---

### Why this is a problem

#### 1) The database cannot enforce correctness

If courses are stored as text:

- you can misspell: `"Databse"`
    
- you can create duplicates: `"Databases, Databases"`
    
- you can invent invalid values: `"Wizardry 101"`
    

The database cannot protect you.

---

#### 2) The database cannot reliably connect data

If “Databases” exists as a course in a `Courses` table, the `Courses` column is not actually connected to it.

It’s just text.

So the relationship is an illusion.

---

#### 3) Searching and updating becomes messy

Even if we _don’t_ teach querying yet, the concept is important:

A list in a column makes almost every future operation harder:

- adding a course means editing a string
    
- removing a course means editing a string
    
- avoiding duplicates becomes painful
    
- ensuring consistency becomes unreliable
    

It turns database design into text editing.

---

### Fix: Use a junction table for many-to-many relationships

If a student can have multiple courses,  
and a course can have multiple students,  
then we are dealing with **many-to-many**.

✅ The relational model solves many-to-many using a **junction table**:

- Students
    
- Courses
    
- Enrollments (junction)
    

**PostgreSQL design example:**

```sql
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  course_id  INTEGER NOT NULL REFERENCES courses(course_id),
  PRIMARY KEY (student_id, course_id)
);
```

This design ensures:

- every enrollment points to a real student
    
- every enrollment points to a real course
    
- duplicates are prevented by the composite primary key
    

The result is clean and scalable:

You can add 1 course or 1000 courses  
without changing the structure.

---

#  Micro-Mistakes 

### Mistake 4: Treating NULL as “empty string”

- `NULL` means _missing value_
    
- `''` means _a value that is an empty string_
    

They are not the same.

---

### Mistake 5: Avoiding constraints “to keep it simple”

Beginners often skip constraints, thinking they are optional.

But constraints are the database’s superpower:

- they prevent bad data early
    
- they remove burden from application code
    

---

### Mistake 6: Naming confusion (inconsistent names)

Common beginner issue:

- `studentId`, `StudentID`, `student_id` all mixed
    

A consistent naming style makes schemas easier to read and maintain.

✅ PostgreSQL-friendly convention:

- `snake_case` for tables and columns (`student_id`)
    
