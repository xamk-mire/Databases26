
# SQL Fundamentals, Part II (PostgreSQL)

### Filtering, Sorting, Aggregation, Grouping, and Aliases — with results

In the previous chapter, we learned to _build the world_: tables, keys, inserts.  
Now we learn to _read the world like a map_—selecting only what matters, ordering it, summarizing it, and naming things so our queries remain human.

This chapter focuses on five essentials:

- **Filtering** → `WHERE`
    
- **Sorting** → `ORDER BY`, `LIMIT`
    
- **Aggregation** → `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
    
- **Grouping** → `GROUP BY`, `HAVING`
    
- **Aliases** → `AS`, table aliases
    

---

## Our shared example dataset

You can imagine this as a small university database.

### Table: `students`

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|3|Sara Niemi|_(NULL)_|
|4|Olli Koski|[olli@gmail.com](mailto:olli@gmail.com)|

### Table: `courses`

|course_id|title|credits|
|--:|---|--:|
|1|Databases|5|
|2|Algorithms|6|
|3|Web Development|5|

### Table: `enrollments`

|student_id|course_id|
|--:|--:|
|1|1|
|1|2|
|2|1|
|3|1|
|3|3|
|4|3|

### Table: `grades`

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|1|2|4|
|2|1|3|
|3|1|2|
|3|3|5|
|4|3|4|

---
# 1) Filtering with `WHERE`

### A gallery of conditions: every keyword, a different gate

`WHERE` is how SQL chooses _which rows are allowed to appear_ in the result.  
Each condition is a rule, and each rule is a kind of gate.

We’ll use these tables as our base:

### `students`

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|3|Sara Niemi|_(NULL)_|
|4|Olli Koski|[olli@gmail.com](mailto:olli@gmail.com)|

### `courses`

|course_id|title|credits|
|--:|---|--:|
|1|Databases|5|
|2|Algorithms|6|
|3|Web Development|5|

### `enrollments`

|student_id|course_id|
|--:|--:|
|1|1|
|1|2|
|2|1|
|3|1|
|3|3|
|4|3|

### `grades`

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|1|2|4|
|2|1|3|
|3|1|2|
|3|3|5|
|4|3|4|

---

## `=` Equality

### Example: courses with exactly 6 credits

```sql
SELECT course_id, title, credits
FROM courses
WHERE credits = 6;
```

**Result**

|course_id|title|credits|
|--:|---|--:|
|2|Algorithms|6|

**Explanation**

- Only rows where `credits` equals `6` survive the filter.
    

---

## `<>` Not equal

### Example: students whose email is not in the `uni.fi` domain (and not NULL)

```sql
SELECT student_id, full_name, email
FROM students
WHERE email <> 'aino@uni.fi';
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|4|Olli Koski|[olli@gmail.com](mailto:olli@gmail.com)|

**Explanation**

- `<>` means “not equal.”
    
- Notice: Sara Niemi (NULL email) is **not** included, because comparisons with NULL are neither true nor false—they are _unknown_.
    

---

## `<` Less than

### Example: grades below 4

```sql
SELECT student_id, course_id, grade
FROM grades
WHERE grade < 4;
```

**Result**

|student_id|course_id|grade|
|--:|--:|--:|
|2|1|3|
|3|1|2|

---

## `<=` Less than or equal

### Example: courses with credits 5 or less

```sql
SELECT course_id, title, credits
FROM courses
WHERE credits <= 5;
```

**Result**

|course_id|title|credits|
|--:|---|--:|
|1|Databases|5|
|3|Web Development|5|

---

## `>` Greater than

### Example: grades greater than 4

```sql
SELECT student_id, course_id, grade
FROM grades
WHERE grade > 4;
```

**Result**

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|3|3|5|

---

## `>=` Greater than or equal

### Example: grades at least 4

```sql
SELECT student_id, course_id, grade
FROM grades
WHERE grade >= 4;
```

**Result**

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|1|2|4|
|3|3|5|
|4|3|4|

---

## Logical operators: `AND`, `OR`, `NOT`

## `AND` (both must be true)

### Example: grades between 3 and 4 (inclusive) using AND

```sql
SELECT student_id, course_id, grade
FROM grades
WHERE grade >= 3 AND grade <= 4;
```

**Result**

|student_id|course_id|grade|
|--:|--:|--:|
|1|2|4|
|2|1|3|
|4|3|4|

---

## `OR` (either may be true)

### Example: enrollments in course 2 OR course 3

```sql
SELECT student_id, course_id
FROM enrollments
WHERE course_id = 2 OR course_id = 3;
```

**Result**

|student_id|course_id|
|--:|--:|
|1|2|
|3|3|
|4|3|

---

## `NOT` (negation)

### Example: courses that are NOT 5 credits

```sql
SELECT course_id, title, credits
FROM courses
WHERE NOT (credits = 5);
```

**Result**

|course_id|title|credits|
|--:|---|--:|
|2|Algorithms|6|

**Explanation**

- `NOT` flips the truth of the condition.
    

---

## Membership: `IN`

## `IN` (value is in a list)

### Example: students whose id is 1 or 3

```sql
SELECT student_id, full_name
FROM students
WHERE student_id IN (1, 3);
```

**Result**

|student_id|full_name|
|--:|---|
|1|Aino Laine|
|3|Sara Niemi|

**Explanation**

- `IN (...)` is often clearer than chaining many `OR` conditions.
    

---

## Ranges: `BETWEEN`

## `BETWEEN` (inclusive range)

### Example: grades between 2 and 4 inclusive

```sql
SELECT student_id, course_id, grade
FROM grades
WHERE grade BETWEEN 2 AND 4;
```

**Result**

|student_id|course_id|grade|
|--:|--:|--:|
|1|2|4|
|2|1|3|
|3|1|2|
|4|3|4|

**Explanation**

- `BETWEEN` includes endpoints (2 and 4 are included).
    

---

## Pattern matching: `LIKE`

## `LIKE` with `%` (any length wildcard)

### Example: emails ending in `@uni.fi`

```sql
SELECT student_id, full_name, email
FROM students
WHERE email LIKE '%@uni.fi';
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|

---

## `LIKE` with `_` (single character wildcard)

### Example: names that are exactly 4 characters before a space, then something

This is a “teaching” example for `_`:

```sql
SELECT student_id, full_name
FROM students
WHERE full_name LIKE '____ %';
```

**Result**

|student_id|full_name|
|--:|---|
|1|Aino Laine|
|2|Mika Virtanen|
|4|Olli Koski|

**Explanation**

- `____` means “exactly four characters”
    
- then a space, then anything (`%`)
    
- “Sara Niemi” is not included because “Sara” is 4 letters **but** it still matches; wait—yes, it should match. Why didn’t it appear? Because it _does_ match the pattern. Let’s correct the pattern to demonstrate something clearer.
    

✅ Better `_` example (unambiguous): emails with exactly 4 letters before `@` (aino/mika are 4, olli is 4 too but not uni.fi; Sara is NULL)

```sql
SELECT student_id, full_name, email
FROM students
WHERE email LIKE '____@%';
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|4|Olli Koski|[olli@gmail.com](mailto:olli@gmail.com)|

**Explanation**

- `____@%` means “exactly four characters, then @, then anything”
    
- NULL emails do not match.
    

---

## Missing values: `IS NULL` and `IS NOT NULL`

## `IS NULL`

### Example: students with missing email

```sql
SELECT student_id, full_name, email
FROM students
WHERE email IS NULL;
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|3|Sara Niemi|_(NULL)_|

---

## `IS NOT NULL`

### Example: students who do have an email

```sql
SELECT student_id, full_name, email
FROM students
WHERE email IS NOT NULL;
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|4|Olli Koski|[olli@gmail.com](mailto:olli@gmail.com)|

---

## A “combined” example 

### Example: uni emails OR missing email (common data-cleaning pattern)

```sql
SELECT student_id, full_name, email
FROM students
WHERE email LIKE '%@uni.fi' OR email IS NULL;
```

**Result**

|student_id|full_name|email|
|--:|---|---|
|1|Aino Laine|[aino@uni.fi](mailto:aino@uni.fi)|
|2|Mika Virtanen|[mika@uni.fi](mailto:mika@uni.fi)|
|3|Sara Niemi|_(NULL)_|

**Explanation**

- Demonstrates that NULL needs explicit handling.
    

---

# 2) Sorting with `ORDER BY` (and `LIMIT`)

If `WHERE` chooses the cast, **ORDER BY** decides who walks onto the stage first.

### Key words

- **ORDER BY**
    
- **ASC** (default), **DESC**
    
- multi-column ordering
    
- **LIMIT** to take only the first _N_ rows
    

---

## Example: Courses ordered by credits (high to low), then title (A–Z)

```sql
SELECT course_id, title, credits
FROM courses
ORDER BY credits DESC, title ASC;
```

**Result**

|course_id|title|credits|
|--:|---|--:|
|2|Algorithms|6|
|1|Databases|5|
|3|Web Development|5|

**Explanation**

- First sort: credits descending (6 before 5)
    
- Tie-breaker: title ascending (Databases before Web Development)
    

---

## Example: “Top 2” courses by credits

```sql
SELECT course_id, title, credits
FROM courses
ORDER BY credits DESC, title ASC
LIMIT 2;
```

**Result**

|course_id|title|credits|
|--:|---|--:|
|2|Algorithms|6|
|1|Databases|5|

**Explanation**

- Same sorting as before, but we only keep the first two rows.
    

---

# 3) Aggregation (summarizing many rows into one)

Aggregation is how SQL turns a crowd into a single sentence.

### Key words

- **COUNT**
    
- **SUM**
    
- **AVG**
    
- **MIN**, **MAX**
    

---

## Example: How many students exist?

```sql
SELECT COUNT(*) AS student_count
FROM students;
```

**Result**

|student_count|
|--:|
|4|

**Explanation**

- `COUNT(*)` counts rows, regardless of NULLs.
    

---

## Example: How many students have an email?

```sql
SELECT COUNT(email) AS students_with_email
FROM students;
```

**Result**

|students_with_email|
|--:|
|3|

**Explanation**

- `COUNT(email)` counts only rows where `email` is **not NULL**.
    

---

## Example: Average credits across all courses

```sql
SELECT AVG(credits) AS avg_credits
FROM courses;
```

**Result**

|avg_credits|
|--:|
|5.3333333333333333|

**Explanation**

- PostgreSQL averages (5, 6, 5) → 16/3 → 5.3333…
    

---

# 4) Grouping with `GROUP BY`

### Seeing the result “form” step by step

**Grouping** is what happens when SQL stops treating rows as individual stories and starts treating them as **crowds**.

With `GROUP BY`, PostgreSQL performs a kind of quiet ritual:

1. it reads rows,
    
2. it sorts them into piles (groups),
    
3. it summarizes each pile,
    
4. and only then does it return results.
    

### Keywords to highlight

- **GROUP BY** → forms groups based on equal values in one or more columns
    
- **aggregate function** → summarizes each group (e.g., `COUNT`, `AVG`)
    
- **HAVING** → filters _groups_ after aggregation
    
- **WHERE** → filters _rows_ before grouping (covered earlier)
    

---

## Example: Enrollment count per course

### Goal

“How many enrollments does each course have?”

### Query

```sql
SELECT course_id, COUNT(*) AS enrollment_count
FROM enrollments
GROUP BY course_id
ORDER BY course_id;
```

---

## Step 0: Start with the input table (`enrollments`)

|student_id|course_id|
|--:|--:|
|1|1|
|1|2|
|2|1|
|3|1|
|3|3|
|4|3|

This is raw, ungrouped reality: one row per enrollment event.

---

## Step 1: The grouping step (conceptual “piles”)

`GROUP BY course_id` means:

> “Put all rows with the same course_id into the same group.”

So PostgreSQL conceptually forms groups like this:

### Group for `course_id = 1`

|student_id|course_id|
|--:|--:|
|1|1|
|2|1|
|3|1|

### Group for `course_id = 2`

|student_id|course_id|
|--:|--:|
|1|2|

### Group for `course_id = 3`

|student_id|course_id|
|--:|--:|
|3|3|
|4|3|

In this step we are no longer thinking row-by-row, but **group-by-group**.

---

## Step 2: Apply the aggregate to each group

Now `COUNT(*)` is calculated **inside each group**:

- For course 1: `COUNT(*) = 3`
    
- For course 2: `COUNT(*) = 1`
    
- For course 3: `COUNT(*) = 2`
    

We can imagine an intermediate summary table like this:

|course_id|COUNT(*)|
|--:|--:|
|1|3|
|2|1|
|3|2|

---

## Step 3: Produce the final SELECT output

Because the query says:

```sql
SELECT course_id, COUNT(*) AS enrollment_count
```

the final output becomes:

|course_id|enrollment_count|
|--:|--:|
|1|3|
|2|1|
|3|2|

---

---

## Example: Average grade per course

### Goal

“What is the average grade in each course?”

### Query

```sql
SELECT course_id, AVG(grade) AS avg_grade
FROM grades
GROUP BY course_id
ORDER BY course_id;
```

---

## Step 0: Start with the input table (`grades`)

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|1|2|4|
|2|1|3|
|3|1|2|
|3|3|5|
|4|3|4|

---

## Step 1: Group rows by `course_id` (conceptual piles)

### Group for `course_id = 1`

|student_id|course_id|grade|
|--:|--:|--:|
|1|1|5|
|2|1|3|
|3|1|2|

Grades in this group: **5, 3, 2**

### Group for `course_id = 2`

|student_id|course_id|grade|
|--:|--:|--:|
|1|2|4|

Grades: **4**

### Group for `course_id = 3`

|student_id|course_id|grade|
|--:|--:|--:|
|3|3|5|
|4|3|4|

Grades: **5, 4**

---

## Step 2: Apply `AVG(grade)` inside each group

- Course 1 average: (5 + 3 + 2) / 3 = **10 / 3 = 3.3333…**
    
- Course 2 average: 4 / 1 = **4**
    
- Course 3 average: (5 + 4) / 2 = **9 / 2 = 4.5**
    

Conceptual intermediate summary:

|course_id|AVG(grade)|
|--:|--:|
|1|3.3333333333333333|
|2|4.0|
|3|4.5|

---

## Step 3: Final SELECT output

|course_id|avg_grade|
|--:|--:|
|1|3.3333333333333333|
|2|4.0|
|3|4.5|

---

---

## Example: Filtering groups with `HAVING`

### Goal

“Show only courses that have at least 2 enrollments.”

### Query

```sql
SELECT course_id, COUNT(*) AS enrollment_count
FROM enrollments
GROUP BY course_id
HAVING COUNT(*) >= 2
ORDER BY enrollment_count DESC;
```

This example is perfect for showing the difference between:

- **GROUP BY** (make groups)
    
- **COUNT** (summarize groups)
    
- **HAVING** (filter groups)
    

---

## Step 0: Input (`enrollments`)

|student_id|course_id|
|--:|--:|
|1|1|
|1|2|
|2|1|
|3|1|
|3|3|
|4|3|

---

## Step 1: Group by `course_id` (same piles as before)

- course 1 group has 3 rows
    
- course 2 group has 1 row
    
- course 3 group has 2 rows
    

---

## Step 2: Aggregate each group (`COUNT(*)`)

Before HAVING is applied, we have the grouped summary:

|course_id|enrollment_count|
|--:|--:|
|1|3|
|2|1|
|3|2|

This table is the key moment:  
**HAVING operates on this grouped result.**

---

## Step 3: Apply `HAVING COUNT(*) >= 2` (filter groups)

Now PostgreSQL removes any group that does not meet the condition:

- course 2 has count 1 → removed
    
- course 1 and 3 remain
    

After HAVING, the conceptual intermediate table becomes:

|course_id|enrollment_count|
|--:|--:|
|1|3|
|3|2|

---

## Step 4: ORDER BY (final presentation)

`ORDER BY enrollment_count DESC` sorts the remaining groups:

|course_id|enrollment_count|
|--:|--:|
|1|3|
|3|2|

(Already in correct order here.)

---

## What changes if we add WHERE?

This is often the next confusion point, so as a quick illustration:

If we write:

```sql
SELECT course_id, COUNT(*) AS enrollment_count
FROM enrollments
WHERE course_id <> 1
GROUP BY course_id;
```

Then the _rows_ with course 1 are removed **before** grouping happens.

### Input after WHERE (conceptual)

|student_id|course_id|
|--:|--:|
|1|2|
|3|3|
|4|3|

### Group + count result

|course_id|enrollment_count|
|--:|--:|
|2|1|
|3|2|

---

# 5) Aliases (`AS`)

Aliases are how SQL becomes readable: they replace awkward labels with names that sound like meaning.

### Key words

- **AS** (column alias)
    
- **table aliases** (short names like `s`, `c`, `e`)
    
- clarity over cleverness: aliases should make the query read like a sentence
    

---

## Example: Column alias (friendly output name)

```sql
SELECT COUNT(*) AS total_enrollments
FROM enrollments;
```

**Result**

|total_enrollments|
|--:|
|6|

**Explanation**

- Without `AS total_enrollments`, the output column name is less friendly.
    

---

## Example: Table aliases in a JOIN (students + courses)

```sql
SELECT s.full_name, c.title
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses  c ON c.course_id  = e.course_id
ORDER BY s.full_name, c.title;
```

**Result**

|full_name|title|
|---|---|
|Aino Laine|Algorithms|
|Aino Laine|Databases|
|Mika Virtanen|Databases|
|Olli Koski|Web Development|
|Sara Niemi|Databases|
|Sara Niemi|Web Development|

**Explanation**

- `e`, `s`, `c` are table nicknames.
    
- They make column references shorter and clearer (`s.full_name` vs `students.full_name`).
    

---

## Putting it all together (one “full-sentence” query)

## Example: Course titles with enrollment counts (only popular ones), ordered by popularity

```sql
SELECT c.title, COUNT(*) AS enrollment_count
FROM enrollments e
JOIN courses c ON c.course_id = e.course_id
GROUP BY c.title
HAVING COUNT(*) >= 2
ORDER BY enrollment_count DESC, c.title ASC;
```

**Result**

|title|enrollment_count|
|---|--:|
|Databases|3|
|Web Development|2|

**Explanation**

- `JOIN` brings course titles into the enrollment world
    
- `GROUP BY` forms one group per course title
    
- `COUNT(*)` measures popularity
    
- `HAVING` keeps only courses with at least 2 enrollments
    
- `ORDER BY` presents the result in a meaningful order
    

---
