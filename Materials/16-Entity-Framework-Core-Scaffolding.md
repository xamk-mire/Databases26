## Entity Framework Core Scaffolding: Introduction

### Generating DbContext and entities from an existing database

This material is a follow-up to `13-Entity-Framework-Core.md` and `15-Entity-Framework-Core-Migrations.md`. It focuses on **scaffolding** – the process where EF Core reads an existing database schema and generates:

- A `DbContext` class
- C# entity classes that map to tables and views

This style is often called **database-first** or **reverse engineering**. It is useful when:

- The database already exists (legacy system or shared corporate database).
- You want to **start from an existing schema** instead of designing the model in C# first.
- The database is managed by another team and your job is to build an app that uses it.

---

## 1) Code-First vs Database-First vs Hybrid

EF Core supports three common approaches:

- **Code-first**:
  - You design the model in C# (entities, relationships, configurations).
  - EF Core uses migrations to create and evolve the database schema.

- **Database-first (scaffolding)**:
  - The database schema already exists.
  - EF Core reads the schema and generates C# code that matches it.

- **Hybrid**:
  - You might scaffold once from a database.
  - Then you continue to evolve the model with code-first and migrations.

This material focuses on **database-first** scaffolding, but you can combine it with code-first techniques later if desired.

---

## 2) What Scaffolding Does (and Does Not Do)

### What scaffolding does

When you run the scaffolding command, EF Core:

- Connects to an existing database (using a connection string and provider).
- Reads:
  - Tables
  - Views
  - Primary keys and foreign keys
  - Column types and nullability
  - Indexes and constraints
- Generates:
  - A `DbContext` class with `DbSet<T>` properties for tables/views.
  - Entity classes with properties and navigation properties.
  - Configuration (via Fluent API or attributes, depending on provider and options).

### What scaffolding does _not_ do

Scaffolding does **not**:

- Automatically keep your model and database in sync after the initial generation.
- Maintain your custom business logic or annotations if you re-scaffold without care.
- Solve database design issues (e.g., missing keys, inconsistent types).

You, as the developer, must:

- Decide **how often to re-scaffold** (if the database changes).
- Protect or reapply your manual changes when regenerating.

---

## 3) Prerequisites for Scaffolding

Before scaffolding, you need:

- A **.NET project** (console app, web API, etc.) that will contain the generated code.
- **EF Core 10** and a provider package installed, for example:

For PostgreSQL:

```bash
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
```

For SQL Server:

```bash
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
dotnet add package Microsoft.EntityFrameworkCore.Design
```

For SQLite:

```bash
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
dotnet add package Microsoft.EntityFrameworkCore.Design
```

And EF Core tools:

```bash
dotnet tool install --global dotnet-ef
```

> **Note:** Run `dotnet ef` commands from the folder containing your `.csproj`, or specify `--project`.

You also need:

- Access to the **database server**.
- A **connection string** for the database you want to reverse engineer.

---

## 4) Basic Scaffolding Command

The core command is:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" <PROVIDER>
```

Examples:

- PostgreSQL:

```bash
dotnet ef dbcontext scaffold "Host=localhost;Database=university;Username=app;Password=secret" Npgsql.EntityFrameworkCore.PostgreSQL
```

- SQL Server:

```bash
dotnet ef dbcontext scaffold "Server=localhost;Database=University;Trusted_Connection=True;TrustServerCertificate=True" Microsoft.EntityFrameworkCore.SqlServer
```

- SQLite:

```bash
dotnet ef dbcontext scaffold "Data Source=university.db" Microsoft.EntityFrameworkCore.Sqlite
```

After running this, EF Core:

- Generates a `DbContext` (by default named after the database, e.g., `UniversityContext`).
- Generates entity classes for all tables it can discover.

---

## 5) Useful Options for Scaffolding

The scaffolding command has many options. Common ones:

### Output directories

Separate context and entities:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --context-dir Data \
  --output-dir Models
```

This will:

- Place the `DbContext` class in the `Data` folder.
- Place entity classes in the `Models` folder.

### Limit to certain tables

If you only need some tables:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --table Students \
  --table Courses \
  --output-dir Models
```

You can specify multiple `--table` options.

### Use data annotations vs Fluent API

By default, EF Core uses Fluent API in `OnModelCreating`. To use data annotations where possible:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --data-annotations
```

### Namespace and context name

Specify a custom `DbContext` name:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --context UniversityDbContext
```

Or a custom root namespace (if not inferred as desired):

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --namespace UniversityApp.Data
```

> For a full list of options: run `dotnet ef dbcontext scaffold --help`.

---

## 6) The Generated DbContext and Entities

After scaffolding, you typically see:

- A `DbContext` similar to:

```csharp
public partial class UniversityDbContext : DbContext
{
    public UniversityDbContext()
    {
    }

    public UniversityDbContext(DbContextOptions<UniversityDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Student> Students { get; set; } = null!;
    public virtual DbSet<Course> Courses { get; set; } = null!;

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        if (!optionsBuilder.IsConfigured)
        {
            // Connection string configuration (often removed and moved to appsettings)
        }
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Fluent configuration generated from database schema
    }
}
```

- Entity classes with properties mapping to columns, e.g.:

```csharp
public partial class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string? Email { get; set; }

    public virtual ICollection<Enrollment> Enrollments { get; set; } = new List<Enrollment>();
}
```

> **Note:** Generated classes are often `partial` so you can extend them in separate files without losing changes when re-scaffolding.

---

## 7) Cleaning Up the Generated Code

Immediately after scaffolding, it is common to:

- **Move the connection string** out of `OnConfiguring` and into configuration (`appsettings.json`, environment variables).
- **Integrate the `DbContext` with dependency injection**, e.g., in ASP.NET Core:

```csharp
builder.Services.AddDbContext<UniversityDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
```

- **Review naming**:
  - Class names
  - Property names (e.g., `full_name` → `FullName`)
  - Navigation properties (e.g., `Enrollments` collection)

- **Decide where to put custom logic**:
  - Add business logic in **partial classes or separate files**.
  - Avoid editing the generated file directly if you plan to re-scaffold.

---

## 8) Re-Scaffolding When the Database Changes

In a database-first workflow, the database schema may change over time (e.g., a DBA adds a new table or column). You might then:

- Re-run scaffolding to update the model.

However, this can overwrite generated files. To avoid losing manual changes:

- Prefer using:
  - Separate partial classes for additional properties and methods.
  - Separate configuration classes `(IEntityTypeConfiguration<T>)` for custom configuration.
- When re-scaffolding, consider:
  - Using `--force` only when you understand what will be overwritten.
  - Committing current code to source control so you can see the diff and restore anything lost.

Example re-scaffold command with overwrite:

```bash
dotnet ef dbcontext scaffold "<CONNECTION_STRING>" Npgsql.EntityFrameworkCore.PostgreSQL \
  --output-dir Models \
  --context-dir Data \
  --context UniversityDbContext \
  --force
```

> **Tip:** Re-scaffolding is easier when you keep your custom code in separate partials or separate layers (e.g., DTOs, services).

---

## 9) Combining Scaffolding with Migrations (Hybrid Approach)

You are not forced to stay purely database-first forever. A common **hybrid** workflow:

1. **Start with scaffolding** from an existing database:
   - Quickly get a working `DbContext` and entities.
2. **Introduce migrations**:
   - Once EF Core “owns” the model, you start making changes in code and using `dotnet ef migrations add` and `dotnet ef database update`.
3. **Coordinate with DBAs**:
   - Define a process for schema changes (who changes what, in which direction).

Key idea:

- Scaffolding is a **starting point** for EF Core models when a database already exists.
- Migrations are a **continuous evolution** tool once your model is in code.

---

## 10) Best Practices and Common Pitfalls

### Best practices

- **Use partial classes**  
  Extend generated entities using partial classes so re-scaffolding does not destroy your custom code.

- **Move configuration into startup**  
  Do not keep real connection strings in generated `OnConfiguring`. Use configuration files and DI instead.

- **Generate into dedicated folders**  
  Use `--output-dir` and `--context-dir` so that generated code is clearly separated from hand-written code.

- **Be explicit about tables**  
  If the database is large, scaffold only the tables you actually need with `--table`.

- **Version control everything**  
  Commit scaffolding changes so you can review diffs and revert mistakes.

### Common pitfalls

- **Editing generated files and then re-scaffolding with `--force`**  
  This can silently remove your changes. Use partial classes and separate files for your logic.

- **Forgetting provider-specific behavior**  
  Different databases (PostgreSQL, SQL Server, SQLite) map types differently; always review generated types for correctness.

- **Leaking connection strings**  
  Avoid hardcoding credentials in code; use secure configuration instead.

- **Big schemas → lots of code**  
  Scaffolding a huge database may generate hundreds of classes; consider limiting to needed tables.

---

## 11) Summary

EF Core scaffolding is the main tool for **reverse engineering an existing database** into a usable EF Core model:

- **`dotnet ef dbcontext scaffold`** connects to a database and generates a `DbContext` and entities.
- You can control which tables, namespaces, and output directories are used.
- Generated code is a **starting point** that you should review, clean up, and integrate into your application architecture.
- By using partial classes, configuration through DI, and careful re-scaffolding, you can safely maintain a database-first or hybrid workflow.

Scaffolding lets you benefit from EF Core even when the database was not originally designed with EF Core in mind.
