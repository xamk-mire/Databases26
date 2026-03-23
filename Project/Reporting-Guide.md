# Reporting Guide — Recipe / Meal Planner Project

The report complements your deliverables by documenting your design choices and showing that your implementation works. Use **screenshots** to demonstrate results and **text** to explain your reasoning.

---

## Purpose of the Report

- Show that your database and application work as intended
- Explain **why** you made specific design decisions
- Demonstrate that you understand the requirements and can justify your implementation
- Help assessors follow your work quickly

---

## Report Format

- **Format:** PDF or Markdown (e.g. `REPORT.md` or `REPORT.pdf`)
- **Length:** Focus on clarity over length. A typical report might be 3–6 pages (PDF) for basic + advanced; add 1–2 pages if you include the ORM stage.
- **Structure:** Follow the sections below. Include only sections for the stages you completed.

---

## Screenshot Guidelines

- **Resolution:** Use clear, readable screenshots. Avoid very small or heavily compressed images.
- **Context:** Include enough context (e.g. query, result set, tool name) so the reader understands what is shown.
- **Captions:** Add a short caption or label below each screenshot.
- **What to capture:**
  - ER diagram (or export it as a separate image and refer to it)
  - Schema execution (e.g. successful creation of tables)
  - Sample query results
  - Index definitions, role definitions
  - Console application output
- **Sensitivity:** Do not include real passwords or sensitive data in screenshots. Use placeholders or blur if needed.

---

# Report Structure

## 1. Introduction

**What to include:**

- Brief project overview (1–2 sentences)
- Which stages you completed (basic, advanced, ORM)
- Any assumptions you made about the requirements
- Link to your github repository
  - If done in a group all members github repository links must be included

**Screenshots:** None required.

---

## 2. Basic Stage

### 2.1 ER Diagram and Design Choices

**Include:**

- Your ER diagram (screenshot or embedded image)
- **Reasoning:** Explain your main design decisions, for example:
  - How you modelled the relationships between entities (cardinality, optionality)
  - How you represented links between entities that carry additional attributes
  - How you decided which attributes are mandatory vs optional

**Questions to address:**

- Why did you structure the relationships between entities the way you did?
- What alternatives did you consider, and why did you choose this approach?

### 2.2 Schema Implementation

**Include:**

- Screenshot of schema creation (e.g. successful execution of your schema script)
- **Reasoning:** Explain key implementation choices, for example:
  - Your choice of data types for different kinds of data
  - Constraints you added and why
  - How you implemented primary keys, foreign keys, and referential integrity (what happens when a row is updated or deleted)

**Questions to address:**

- Why did you choose these data types?
- How did you handle referential integrity when a referenced row is deleted?

### 2.3 Seed Data and Queries

**Include:**

- Screenshot of a representative query result
- **Reasoning:** Explain how your seed data satisfies the project requirements.
- If any query was challenging, explain your approach and how you solved it.

**Questions to address:**

- How does your seed data demonstrate the key relationships in your design?
- Which query was most challenging, and how did you solve it?

---

## 3. Advanced Stage (if completed)

### 3.1 Extended Design and ER Diagram

**Include:**

- Updated ER diagram including all new entities
- **Reasoning:** Explain how you modelled:
  - User types or roles and how they relate
  - The new entities and their relationships to existing ones
  - Any attributes that store additional information (e.g. slots, dates, ordering)

**Questions to address:**

- How did you model user types or roles?
- How did you design the links between the new entities and existing ones?

### 3.2 Schema Extensions, Indexes, and Roles

**Include:**

- Screenshot of schema extensions running successfully
- Screenshot or list of indexes and roles you created
- **Reasoning:** Explain:
  - Why you added specific indexes and what they support
  - How you assigned privileges to each role
  - Your choices for referential integrity in the new tables

**Questions to address:**

- What indexes did you add, and what use cases do they support?
- How did you decide the privilege level for each role?

### 3.3 Advanced Queries

**Include:**

- Screenshot of at least one advanced query result
- **Reasoning:** If a query required special handling, explain your approach.

---

## 4. Console Application — ORM Stage (if completed)

### 4.1 Technology and Setup

**Include:**

- Screenshot of the application running
- **Reasoning:** Explain:
  - Which technology you used and why
  - How you configured the database connection
  - How you mapped your database schema to code (generated vs hand-written)

**Questions to address:**

- How did you connect the application to your database?
- How did you manage configuration (e.g. connection strings, secrets)?

### 4.2 Functionality

**Include:**

- Screenshots of the application showing it reading and displaying data
- **Reasoning:** Explain how the ORM is used to query data and any mapping challenges you faced.

**Questions to address:**

- How does your application fetch and display the required data?
- Did you encounter any mapping issues between your schema and the ORM?

---

## 5. Summary and Reflection

**Include:**

- Short summary of what you built and how it meets the requirements
- Any limitations or improvements you would make if you had more time
- What you learned from the project

**Screenshots:** None required.

---

## Checklist Before Submitting

- All screenshots are clear and have captions
- No sensitive data (passwords, real emails) in screenshots
- Each stage you completed has a corresponding section with reasoning
- Design choices are explained, not just described
- Report is readable (spelling, structure, formatting)

---

## Optional: Report Template

You can start from this structure and fill in the content:

```markdown
# Recipe / Meal Planner Project Report

## 1. Introduction
[Your overview and assumptions]

## 2. Basic Stage
### 2.1 ER Diagram and Design Choices
[Diagram + reasoning]
### 2.2 Schema Implementation
[Screenshot + reasoning]
### 2.3 Seed Data and Queries
[Screenshot + reasoning]

## 3. Advanced Stage (if completed)
### 3.1 Extended Design
### 3.2 Schema, Indexes, Roles
### 3.3 Advanced Queries

## 4. Console Application (if completed)
### 4.1 Technology and Setup
### 4.2 Functionality

## 5. Summary and Reflection
```

