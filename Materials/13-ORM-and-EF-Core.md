# Entity Framework Core: Introduction

### A practical introduction to .NET's ORM for database access

This material is a follow-up to [Databases in Programming](12-Databases-in-Programming.md). 

---

## 1) Introduction to Object-Relational Mappers (ORMs)

### The impedance mismatch

Relational databases store data in **tables, rows, and columns**. Programming languages work with **objects, properties, and references**. These models do not align naturally:

- A database row might map to an object, but relationships are expressed as foreign keys, not object references.
- Nullability, types, and naming conventions differ between SQL and C#.
- Writing SQL by hand for every operation leads to repetitive, error-prone code.

### What an ORM does

An **Object-Relational Mapper (ORM)** sits between your application code and the database. It:

| Responsibility | What it means |
|----------------|---------------|
| **Mapping** | Translates between database rows/columns and programming-language objects |
| **Query generation** | Converts object-oriented or LINQ-style queries into SQL |
| **Change tracking** | Knows which objects are new, modified, or unchanged so it can generate the right INSERT/UPDATE/DELETE |
| **Relationship handling** | Loads related entities (e.g., a student’s enrollments) and manages foreign keys |

You write code in terms of **objects and LINQ**; the ORM generates and executes the SQL.

### ORMs across languages

Different ecosystems have different ORMs:

| Language | Example ORMs |
|----------|--------------|
| C# / .NET | Entity Framework Core, Dapper |
| Java | Hibernate, JPA |
| Python | SQLAlchemy, Django ORM |
| JavaScript/TypeScript | TypeORM, Prisma, Sequelize |
| Ruby | ActiveRecord |

Each has its own conventions, but the core idea is the same: work with objects, let the ORM handle SQL.

### Benefits and tradeoffs

**Benefits:**

- **Productivity** — less boilerplate for CRUD and common queries
- **Type safety** — compile-time checking of property names and types
- **Abstraction** — switch databases or schema without rewriting every query
- **Consistency** — parameterized queries by default, reducing SQL injection risk

**Tradeoffs:**

- **Control** — generated SQL may not be optimal for complex or performance-critical cases
- **Learning curve** — you must understand both the ORM and the underlying SQL
- **Debugging** — when a query behaves unexpectedly, you need to inspect the generated SQL

Knowing when to use the ORM and when to drop to raw SQL is an important skill.

---

## 2) What Is Entity Framework Core?

### EF Core: the .NET ORM

**Entity Framework Core (EF Core)** is Microsoft’s ORM for .NET. It is the successor to Entity Framework 6 (which targeted .NET Framework) and is built for modern .NET (Core and beyond).

This material targets **EF Core 10**, released in November 2025. EF Core 10 is a Long Term Support (LTS) release, supported until November 2028. It requires **.NET 10** to build and run.

### Core building blocks

- **Entity** — a C# class that maps to a database table
- **DbContext** — the central object that represents a session with the database and tracks entities
- **DbSet&lt;T&gt;** — a typed collection representing a table (e.g., `DbSet<Student>` for the `Students` table)

EF Core supports multiple database providers (SQL Server, PostgreSQL, SQLite, MySQL, and others). You write the same C# code; the provider translates it to the database’s SQL dialect.

### Why use EF Core?

| Benefit | What it means |
|---------|---------------|
| Work with objects, not SQL strings | Write `context.Students.Where(s => s.Email == email)` instead of manual SQL |
| Type safety | Compile-time checking of property names and types |
| Migrations | Schema changes are versioned and applied as code |
| Cross-database support | Switch providers (e.g., SQLite for dev, PostgreSQL for prod) without rewriting queries |
| LINQ integration | Use C# LINQ for filtering, projection, and aggregation |

---

## 3) Core Concepts: Entities, DbContext, and DbSet

### Entities

An **entity** is a C# class whose instances correspond to rows in a table. By convention:

- The class name maps to the table name (e.g., `Student` → `Students`)
- Public properties map to columns

```csharp
public class Student
{
    public int Id { get; set; }           // Primary key (convention: "Id" or "ClassNameId")
    public string FullName { get; set; }  = string.Empty;
    public string? Email { get; set; }
}
```

```csharp
public class Course
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public int Credits { get; set; }
}
```

### DbContext

The **DbContext** is the main entry point for database operations. You create a class that inherits from `DbContext` and expose `DbSet<T>` properties for each table.

```csharp
public class UniversityDbContext : DbContext
{
    public DbSet<Student> Students => Set<Student>();
    public DbSet<Course> Courses => Set<Course>();

    public UniversityDbContext(DbContextOptions<UniversityDbContext> options)
        : base(options)
    {
    }
}
```

The `DbContext`:

- Manages connections to the database
- Tracks entities (knows which are new, modified, or unchanged)
- Translates LINQ queries to SQL
- Executes `SaveChanges()` to persist inserts, updates, and deletes

### DbSet

A **DbSet&lt;T&gt;** represents a table. You use it to query and modify data:

```csharp
// Query
var student = await context.Students.FindAsync(1);
var students = await context.Students.Where(s => s.Email != null).ToListAsync();

// Add
context.Students.Add(new Student { FullName = "Aino Laine", Email = "aino@uni.fi" });
await context.SaveChangesAsync();
```

---

## 4) Setting Up EF Core 10 in a Project

### Prerequisites

EF Core 10 requires **.NET 10**. Ensure you have the .NET 10 SDK installed:

```bash
dotnet --version
# Should report 10.x.x or higher
```

### Install packages

For a typical web API or console app, you need:

1. **EF Core provider** — for the database you use (e.g., PostgreSQL, SQL Server, SQLite)
2. **Design-time tools** — for migrations (optional but recommended)

Example for PostgreSQL (EF Core 10):

```bash
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
```

Example for SQLite (simple local development):

```bash
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
dotnet add package Microsoft.EntityFrameworkCore.Design
```

These commands install the latest compatible versions. For EF Core 10, use packages version **10.0.x** (they follow the EF Core version).

Install EF Core tools globally (for migrations):

```bash
dotnet tool install --global dotnet-ef
```

To update to the latest EF Core tools: `dotnet tool update --global dotnet-ef`

**Note for multi-targeted projects:** In EF Core 10, if your project targets multiple frameworks (e.g., `net8.0` and `net10.0`), you must specify which framework to use when running EF tools, for example: `dotnet ef migrations add InitialCreate --framework net10.0`

### Configure DbContext

In **ASP.NET Core**, you register the DbContext in `Program.cs` (or `Startup.cs`) and inject it where needed:

```csharp
// Program.cs
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

builder.Services.AddDbContext<UniversityDbContext>(options =>
    options.UseNpgsql(connectionString));
```

For **SQLite**:

```csharp
builder.Services.AddDbContext<UniversityDbContext>(options =>
    options.UseSqlite("Data Source=university.db"));
```

### Connection string

Store the connection string in configuration (e.g., `appsettings.json` or environment variables), not in code:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=university;Username=myuser;Password=mypass"
  }
}
```

---

## 5) Migrations: Schema as Code

EF Core uses **migrations** to create and update the database schema from your entity model.

### Create a migration

After defining or changing entities:

```bash
dotnet ef migrations add InitialCreate
```

This generates a migration class (e.g., `AddStudentsAndCourses`) that contains the SQL (or provider-specific commands) to create or alter tables.

### Apply migrations

To create or update the database:

```bash
dotnet ef database update
```

In development, you can also apply migrations at startup:

```csharp
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<UniversityDbContext>();
    db.Database.Migrate();
}
```

### Workflow

1. Change entities (add a property, add a new entity, change a relationship).
2. Run `dotnet ef migrations add DescriptiveName`.
3. Review the generated migration.
4. Run `dotnet ef database update` (or let the app do it in dev).

Migrations are version-controlled; they let you evolve the schema over time in a repeatable way.

---

## 6) CRUD Operations with EF Core

### Create (Insert)

```csharp
var student = new Student
{
    FullName = "Mika Virtanen",
    Email = "mika@uni.fi"
};

context.Students.Add(student);
await context.SaveChangesAsync();

// After SaveChanges, student.Id is populated (if using identity)
```

### Read (Query)

```csharp
// By primary key
var student = await context.Students.FindAsync(1);

// Filter with LINQ
var withEmail = await context.Students
    .Where(s => s.Email != null)
    .ToListAsync();

// Single or default
var aino = await context.Students
    .FirstOrDefaultAsync(s => s.Email == "aino@uni.fi");
```

Queries are **deferred**: the database is not hit until you enumerate (e.g., `.ToListAsync()`, `await foreach`).

### Update

```csharp
var student = await context.Students.FindAsync(1);
if (student != null)
{
    student.Email = "aino.new@uni.fi";
    await context.SaveChangesAsync();
}
```

EF Core tracks changes. When you modify a tracked entity and call `SaveChanges()`, it generates the appropriate `UPDATE` statement.

### Delete

```csharp
var student = await context.Students.FindAsync(1);
if (student != null)
{
    context.Students.Remove(student);
    await context.SaveChangesAsync();
}
```

---

## 7) Relationships and Navigation Properties

Entities often relate to each other (e.g., a Student enrolls in many Courses). You model this with **navigation properties** and **foreign keys**.

### One-to-many example: Course and Enrollments

```csharp
public class Enrollment
{
    public int Id { get; set; }
    public int StudentId { get; set; }      // Foreign key
    public int CourseId { get; set; }       // Foreign key
    public int? Grade { get; set; }

    public Student Student { get; set; } = null!;   // Navigation property
    public Course Course { get; set; } = null!;
}

public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = string.Empty;
    public string? Email { get; set; }

    public ICollection<Enrollment> Enrollments { get; set; } = new List<Enrollment>();
}
```

### Include related data

Use `.Include()` to load related entities and avoid the N+1 query problem:

```csharp
var studentsWithEnrollments = await context.Students
    .Include(s => s.Enrollments)
        .ThenInclude(e => e.Course)
    .ToListAsync();
```

This produces a query that joins the tables and loads everything in one or a few round trips.

---

## 8) Fluent API and Data Annotations

EF Core infers a lot from conventions. When you need to override or clarify, use **data annotations** or the **Fluent API**.

### Data annotations

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

public class Student
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(200)]
    public string FullName { get; set; } = string.Empty;

    [MaxLength(256)]
    public string? Email { get; set; }

    [Column("enrolled_at")]
    public DateTime EnrolledAt { get; set; }
}
```

### Fluent API (in DbContext)

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Student>(entity =>
    {
        entity.HasKey(e => e.Id);
        entity.Property(e => e.FullName).IsRequired().HasMaxLength(200);
        entity.Property(e => e.Email).HasMaxLength(256);
        entity.Property(e => e.EnrolledAt).HasColumnName("enrolled_at");
    });

    modelBuilder.Entity<Enrollment>()
        .HasOne(e => e.Student)
        .WithMany(s => s.Enrollments)
        .HasForeignKey(e => e.StudentId);
}
```

The Fluent API is often preferred for complex configurations because it keeps entities free of database-specific attributes.

---

## 9) When to Use Raw SQL

EF Core is powerful, but some scenarios benefit from raw SQL:

- Complex reporting or analytics queries
- Database-specific features (e.g., window functions, CTEs)
- Performance-critical paths where you need full control

### Raw SQL with EF Core

For entities, use `FromSqlRaw` or `FromSql`:

```csharp
var students = await context.Students
    .FromSqlRaw("SELECT * FROM students WHERE email LIKE {0}", "%@uni.fi")
    .ToListAsync();
```

For custom types (DTOs) not mapped as entities, use `SqlQuery` (EF Core 10) or `SqlQueryRaw` on `context.Database`:

```csharp
var result = await context.Database
    .SqlQuery<StudentSummary>($"SELECT id, full_name FROM students WHERE id = {studentId}")
    .ToListAsync();
```

With `SqlQuery`, string interpolation is safe: EF Core converts values to parameters. With `FromSqlRaw`, use `{0}`, `{1}`, etc. as placeholders and pass values as additional arguments. **Never** concatenate user input into SQL strings.

---

## 10) Dependency Injection and DbContext Lifetime

### Injecting DbContext

In ASP.NET Core, you typically inject `DbContext` into controllers or services:

```csharp
[ApiController]
[Route("api/[controller]")]
public class StudentsController : ControllerBase
{
    private readonly UniversityDbContext _context;

    public StudentsController(UniversityDbContext context)
    {
        _context = context;
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<Student>> GetStudent(int id)
    {
        var student = await _context.Students.FindAsync(id);
        if (student == null) return NotFound();
        return student;
    }
}
```

### DbContext lifetime

The default lifetime for `AddDbContext` is **scoped**: one instance per HTTP request. That means:

- Each request gets its own `DbContext`
- The instance is disposed when the request ends
- Do not use a single `DbContext` across multiple requests or in background services without creating a new scope

---

## 11) Summary

Entity Framework Core 10 brings ORM benefits to .NET:

- **Entities** — C# classes mapped to tables
- **DbContext** — session with the database, tracks entities, executes queries
- **DbSet&lt;T&gt;** — typed access to a table
- **Migrations** — schema changes as versioned code
- **LINQ** — type-safe, expressive queries with improved translation in EF Core 10
- **Providers** — SQL Server, PostgreSQL, SQLite, and more

EF Core 10 (with .NET 10) adds capabilities such as improved LINQ-to-SQL translation for more .NET methods, named query filters for scenarios like soft deletes and multitenancy, vector search support (SQL Server), and native JSON type support. You work with objects and LINQ; EF Core generates SQL. For complex cases, you can drop to raw SQL while staying within the same framework.

---

## Related materials

- [12 – Databases in Programming](12-Databases-in-Programming.md) — Purpose of databases in programming, ORMs, CRUD, transactions
- [05 – SQL Fundamentals](05-SQL-fundamentals.md) — SQL basics (tables, keys, queries)
- [09 – Transactions and Data Modification](09-Transactions-and-Data-Modification.md) — Transactions in SQL
- [14 – Managing Users and Roles in Programming](14-Managing-Users-and-Roles-in-Programming.md) — Application users, roles, and Identity integration

## Further reading

- [EF Core Documentation](https://learn.microsoft.com/en-us/ef/core/) — Official Microsoft documentation
- [What's New in EF Core 10](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew) — EF Core 10 release notes
