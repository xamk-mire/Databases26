## Entity Framework Core Migrations: Introduction

### Versioning your database schema with code

This material is a follow-up to `13-Entity-Framework-Core.md`. It focuses only on **EF Core migrations**—the mechanism EF Core uses to **create and evolve** the database schema based on your C# entity classes.

The goal is to learn how to:

- **Initialize** a database from your model
- **Track schema changes over time** as versioned migration files
- **Apply and roll back** schema changes in different environments (development, test, production)
- **Avoid common pitfalls** when modifying entities and running migrations

---

## 1) What Are Migrations and Why Use Them?

### The problem: keeping schema and code in sync

In a typical project:

- The **C# model** (entities, `DbContext`, configurations) evolves as you add features.
- The **database schema** (tables, columns, indexes, constraints) must evolve in lockstep.

If changes are done manually in the database (e.g., by running ad-hoc SQL in a GUI tool), you quickly lose track of:

- What changes were made
- In what order
- On which environment

This makes it difficult to:

- Onboard new developers
- Recreate a database from scratch
- Roll back a broken deployment

### The solution: schema as code

**EF Core migrations** treat the schema as **versioned code**:

- Each migration is a **small, ordered step** (e.g., “AddStudentsTable”, “AddEnrollmentCourseRelation”).
- Migrations live in **source control** alongside your application code.
- EF Core keeps a **history table** in the database to track which migrations have been applied.

Benefits:

- **Repeatability**: You can recreate the database from scratch by reapplying all migrations.
- **Traceability**: You can see exactly which changes happened and when.
- **Team-friendly**: Multiple developers can collaborate on schema evolution.

---

## 2) Prerequisites and Setup

Before working with migrations, ensure you have:

- **EF Core 10** packages and a provider installed in your project (see `13-Entity-Framework-Core.md`).
- **EF Core tools** installed:

```bash
dotnet tool install --global dotnet-ef
# or update
dotnet tool update --global dotnet-ef
```

When your project targets multiple frameworks (e.g., `net8.0` and `net10.0`), specify the framework when running tools:

```bash
dotnet ef migrations add InitialCreate --framework net10.0
```

> **Note:** All `dotnet ef` commands must be run from the **project directory** containing your `.csproj` file (or specify `--project`).

---

## 3) The First Migration: InitialCreate

Assume you have:

- A `DbContext` (e.g., `UniversityDbContext`)
- Some entities (e.g., `Student`, `Course`, `Enrollment`)

### Step 1: Add the initial migration

From the project directory:

```bash
dotnet ef migrations add InitialCreate
```

This command:

- Checks your current model (entities + configuration).
- Compares it to the **empty** database.
- Generates a migration file (by default under `Migrations/`).

Typical contents (simplified):

```csharp
public partial class InitialCreate : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Create tables, columns, constraints
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        // Reverse actions from Up (drop tables, etc.)
    }
}
```

### Step 2: Create the database

Apply the migration to the database:

```bash
dotnet ef database update
```

This:

- Executes the `Up` method of all **pending** migrations in order.
- Creates the EF Core migrations history table (by default `__EFMigrationsHistory`).

If the database does not exist yet, EF Core creates it.

---

## 4) How EF Core Tracks Schema Versions

EF Core stores migration information in two places:

- In **code**: migration classes under `Migrations/`
- In the **database**: the `__EFMigrationsHistory` table

Each row in `__EFMigrationsHistory` contains:

- The **migration ID** (e.g., `20260316120000_InitialCreate`)
- The **product version** (e.g., `10.0.0`)

When you run:

```bash
dotnet ef database update
```

EF Core:

1. Reads all migration classes in your project.
2. Checks which ones are already recorded in `__EFMigrationsHistory`.
3. Applies only the **missing** ones, in order.

---

## 5) Typical Migration Workflow During Development

When you modify your model, follow this pattern.

### Step 1: Change the model

Examples:

- Add a property to an entity:

```csharp
public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = string.Empty;
    public string? Email { get; set; }
    public DateTime EnrolledAt { get; set; }  // new property
}
```

- Add a new entity:

```csharp
public class Teacher
{
    public int Id { get; set; }
    public string FullName { get; set; } = string.Empty;
}
```

### Step 2: Add a migration

Use a **descriptive name**:

```bash
dotnet ef migrations add AddStudentEnrolledAt
dotnet ef migrations add AddTeacherEntity
```

This generates new migration files that describe the changes:

- Adding a column (`EnrolledAt`) to `Students`
- Creating a new table (`Teachers`)

### Step 3: Review the migration

Open the generated migration class and check:

- Are table and column names as expected?
- Are nullability and default values correct?
- Are foreign keys and indexes configured as intended?

You can edit the migration if needed (especially for data fixes).

### Step 4: Apply the migration

Update your local database:

```bash
dotnet ef database update
```

Now both:

- The **model** and
- The **database schema**

are in sync at the new version.

---

## 6) Common `dotnet ef` Commands for Migrations

### Add a migration

```bash
dotnet ef migrations add MigrationName
```

Options:

- `--project` – project containing the `DbContext`
- `--startup-project` – project that contains the app entry point (e.g., web API)
- `--context` – choose a specific `DbContext` if you have more than one
- `--output-dir` – customize the folder for migrations (default is `Migrations`)

### Apply migrations (update database)

```bash
dotnet ef database update
```

Optionally specify a target migration:

```bash
dotnet ef database update 20260316120000_InitialCreate
dotnet ef database update InitialCreate
dotnet ef database update 0      # Revert all migrations (drop everything created by migrations)
```

### List migrations

```bash
dotnet ef migrations list
```

Shows:

- Applied migrations
- Pending migrations (not yet applied to the database)

### Remove the last migration (development only)

If you just added a migration but **have not** applied it to any shared database:

```bash
dotnet ef migrations remove
```

This deletes the last migration file and updates the model snapshot. Use this to fix a typo or mistake before committing.

---

## 7) Rolling Back and Targeted Updates

Sometimes you need to:

- Roll back to an earlier schema version
- Apply migrations step by step

### Roll back to a previous migration

To move the database schema **back** to a specific migration:

```bash
dotnet ef database update PreviousMigrationName
```

EF Core:

- Finds which migrations are **after** the target
- Applies their `Down` methods in reverse order

> **Warning:** Rolling back migrations can destroy data (e.g., dropping tables or columns). Use carefully and typically only in development or test.

### Applying migrations in stages

You can specify any migration as the target. EF Core will:

- Apply missing `Up` methods to move **forward**
- Or apply `Down` methods to move **backward**

This is useful during manual deployments where you want explicit control over schema changes.

---

## 8) Seeding Data with Migrations

Sometimes you want **seed data**: initial records required for the application to work (e.g., default roles, admin user, test data).

### Model-based seeding via `OnModelCreating`

One option is using `HasData` in `OnModelCreating`. EF Core then generates insert/update statements inside migrations automatically.

Example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Course>().HasData(
        new Course { Id = 1, Title = "Intro to Databases", Credits = 5 },
        new Course { Id = 2, Title = "Advanced SQL", Credits = 5 }
    );
}
```

When you add a migration after this change, the migration includes appropriate `InsertData` calls.

### Custom data operations in migrations

You can also write custom data changes directly in the migration:

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.Sql(
        "UPDATE Students SET EnrolledAt = CURRENT_TIMESTAMP WHERE EnrolledAt IS NULL");
}
```

Use this carefully:

- Keep logic simple and deterministic.
- Avoid complex application logic in migrations.

---

## 9) Best Practices and Common Pitfalls

### Best practices

- **One feature = one migration (or a few)**  
  Keep migrations small and focused. This makes them easier to review and debug.

- **Always generate migrations from a clean state**  
  Ensure your code compiles and the model is consistent before adding a migration.

- **Review generated migrations**  
  Never blindly trust generated scripts, especially when dropping or renaming columns.

- **Run migrations locally before pushing**  
  Confirm that `dotnet ef database update` succeeds on your machine.

- **Use explicit names**  
  Use meaningful migration names (e.g., `AddEnrollmentTable`, `RenameStudentEmailToUniversityEmail`).

### Common pitfalls

- **Changing entity names without handling data**  
  Renaming an entity or property may result in a drop + create, which can delete data. Use explicit `RenameTable`/`RenameColumn` operations if needed.

- **Editing old migrations that are already applied**  
  Avoid modifying migrations that have been applied to shared databases; instead:
  - Create new migrations to adjust the schema further, or
  - Coordinate carefully with the team if a destructive change is unavoidable.

- **Multiple developers generating overlapping migrations**  
  When working in a team:
  - Pull latest changes before creating new migrations.
  - Resolve conflicts in migration files and the model snapshot carefully.

- **Running tools in the wrong project**  
  If EF Core cannot find the `DbContext`, specify `--project` and/or `--startup-project`.

---

## 10) Migrations in Different Environments

### Development

Common patterns:

- Apply migrations automatically at app startup:

```csharp
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<UniversityDbContext>();
    db.Database.Migrate();
}
```

- Or run `dotnet ef database update` manually whenever you change the model.

### Test / CI (Continuous Integration)

In automated tests:

- Create a fresh database (often with SQLite or a test-specific PostgreSQL/SQL Server instance).
- Apply all migrations before running tests:

```bash
dotnet ef database update
```

Some projects use **in-memory** databases for unit tests and real databases with migrations for integration tests.

### Production

In production, you typically:

- Run `dotnet ef database update` as part of a deployment step, _or_
- Generate SQL scripts and run them via a DBA or deployment pipeline.

Generating a SQL script:

```bash
dotnet ef migrations script
```

Options:

- `dotnet ef migrations script 0 LastMigration` – script from scratch to the latest migration
- `dotnet ef migrations script FromMigration ToMigration` – script only a range

Scripts:

- Can be reviewed by DBAs
- Can be applied with existing database tooling

---

## 11) Summary

EF Core migrations are the core mechanism for **managing schema changes as code**:

- **Migrations** represent incremental, versioned schema changes.
- **`dotnet ef` tools** let you add, inspect, apply, and roll back migrations.
- The **model**, **migration files**, and **database history table** must stay in sync.
- Good habits—small migrations, meaningful names, careful reviews—keep your database evolution reliable and understandable.

Mastering migrations means you can confidently evolve your database schema over time without losing control or breaking environments.
