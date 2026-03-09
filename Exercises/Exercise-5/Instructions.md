# Exercise 5: C# Console Application with Entity Framework Core — University Database

### Set up a simple console application with EF Core connected to the university database

> **Instructions:**  
> Create a C# **console application** that uses **Entity Framework Core** to connect to the **university_db** PostgreSQL database (used throughout the materials). You will define entities that map to the existing schema, configure the DbContext, and implement an **interactive menu** that lets the user choose which query to run (students, courses, grades, enrollments, teachers).
>
> **Prerequisites:**
>
> - .NET 10 SDK
> - PostgreSQL with `university_db` created and populated (see [university_db_schema.sql](./Materials/Example-db/university_db_schema.sql) and [university_db_seed.sql](./Materials/Example-db/university_db_seed.sql))
> - Materials 12 (Databases in Programming), 13 (Entity Framework Core)

---

## Database schema reference

The `university_db` database has the following tables:

| Table           | Columns                                         | Notes                         |
| --------------- | ----------------------------------------------- | ----------------------------- |
| **students**    | student_id (PK), full_name, email               | student_id is IDENTITY        |
| **teachers**    | teacher_id (PK), full_name, email               | teacher_id is IDENTITY        |
| **courses**     | course_id (PK), title, credits, teacher_id (FK) | teacher_id → teachers         |
| **enrollments** | student_id, course_id (composite PK)            | Both FKs; junction table      |
| **grades**      | student_id, course_id (composite PK), grade     | Both FKs; grade 0–5, nullable |

---

## Part A — Create the project and add EF Core

### A1 — Create a new console project

Create a new console application named `UniversityConsole`:

```bash
dotnet new console -n UniversityConsole -o UniversityConsole
cd UniversityConsole
```

### A2 — Add EF Core and configuration packages

Add the PostgreSQL provider, design-time tools, and configuration support (for reading the connection string from `appsettings.json`):

```bash
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.Extensions.Configuration.Json
```

Install the EF Core CLI tools globally (if not already installed):

```bash
dotnet tool install --global dotnet-ef
```

### A3 — Prepare the database

Ensure `university_db` exists and has data:

1. Create the database (if needed): `CREATE DATABASE university_db;`
2. Run [university_db_schema.sql](./Materials/Example-db/university_db_schema.sql) to create tables.
3. Run [university_db_seed.sql](./Materials/Example-db/university_db_seed.sql) to insert sample data.

---

## Part B — Define entities

Create an `Entities` folder and add entity classes that map to the `university_db` tables. Use `[Table]` and `[Column]` attributes to map C# names to the existing snake_case schema.

### B1 — Student entity

```csharp
// Entities/Student.cs
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace UniversityConsole.Entities;

[Table("students")]
public class Student
{
    [Key]
    [Column("student_id")]
    public int StudentId { get; set; }

    [Column("full_name")]
    [MaxLength(100)]
    public required string FullName { get; set; }

    [Column("email")]
    [MaxLength(255)]
    public string? Email { get; set; }

    public ICollection<Enrollment> Enrollments { get; set; } = new List<Enrollment>();
    public ICollection<Grade> Grades { get; set; } = new List<Grade>();
}
```

### B2 — Teacher entity

```csharp
// Entities/Teacher.cs
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace UniversityConsole.Entities;

[Table("teachers")]
public class Teacher
{
    [Key]
    [Column("teacher_id")]
    public int TeacherId { get; set; }

    [Column("full_name")]
    [MaxLength(100)]
    public required string FullName { get; set; }

    [Column("email")]
    [MaxLength(255)]
    public string? Email { get; set; }

    public ICollection<Course> Courses { get; set; } = new List<Course>();
}
```

### B3 — Course entity

```csharp
// Entities/Course.cs
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace UniversityConsole.Entities;

[Table("courses")]
public class Course
{
    [Key]
    [Column("course_id")]
    public int CourseId { get; set; }

    [Column("title")]
    [MaxLength(200)]
    public required string Title { get; set; }

    [Column("credits")]
    public int Credits { get; set; }

    [Column("teacher_id")]
    public int TeacherId { get; set; }

    public Teacher Teacher { get; set; } = null!;
    public ICollection<Enrollment> Enrollments { get; set; } = new List<Enrollment>();
    public ICollection<Grade> Grades { get; set; } = new List<Grade>();
}
```

### B4 — Enrollment entity (composite key)

```csharp
// Entities/Enrollment.cs
using System.ComponentModel.DataAnnotations.Schema;

namespace UniversityConsole.Entities;

[Table("enrollments")]
public class Enrollment
{
    [Column("student_id")]
    public int StudentId { get; set; }

    [Column("course_id")]
    public int CourseId { get; set; }

    public Student Student { get; set; } = null!;
    public Course Course { get; set; } = null!;
}
```

### B5 — Grade entity (composite key)

```csharp
// Entities/Grade.cs
using System.ComponentModel.DataAnnotations.Schema;

namespace UniversityConsole.Entities;

[Table("grades")]
public class Grade
{
    [Column("student_id")]
    public int StudentId { get; set; }

    [Column("course_id")]
    public int CourseId { get; set; }

    [Column("grade")]
    public int? GradeValue { get; set; }

    public Student Student { get; set; } = null!;
    public Course Course { get; set; } = null!;
}
```

**Task B5.1 — Configure composite keys in DbContext**

Enrollment and Grade have composite primary keys. You will configure these in the DbContext in Part C using the Fluent API.

---

## Part C — DbContext and configuration

### C1 — Create UniversityDbContext

Create `Data/UniversityDbContext.cs`:

```csharp
// Data/UniversityDbContext.cs
using Microsoft.EntityFrameworkCore;
using UniversityConsole.Entities;

namespace UniversityConsole.Data;

public class UniversityDbContext : DbContext
{
    public UniversityDbContext(DbContextOptions<UniversityDbContext> options)
        : base(options)
    {
    }

    public DbSet<Student> Students => Set<Student>();
    public DbSet<Teacher> Teachers => Set<Teacher>();
    public DbSet<Course> Courses => Set<Course>();
    public DbSet<Enrollment> Enrollments => Set<Enrollment>();
    public DbSet<Grade> Grades => Set<Grade>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Enrollment>(entity =>
        {
            entity.HasKey(e => new { e.StudentId, e.CourseId });
            entity.HasOne(e => e.Student).WithMany(s => s.Enrollments)
                .HasForeignKey(e => e.StudentId).OnDelete(DeleteBehavior.Restrict);
            entity.HasOne(e => e.Course).WithMany(c => c.Enrollments)
                .HasForeignKey(e => e.CourseId).OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<Grade>(entity =>
        {
            entity.HasKey(g => new { g.StudentId, g.CourseId });
            entity.HasOne(g => g.Student).WithMany(s => s.Grades)
                .HasForeignKey(g => g.StudentId).OnDelete(DeleteBehavior.Restrict);
            entity.HasOne(g => g.Course).WithMany(c => c.Grades)
                .HasForeignKey(g => g.CourseId).OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<Course>()
            .HasOne(c => c.Teacher)
            .WithMany(t => t.Courses)
            .HasForeignKey(c => c.TeacherId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
```

### C2 — Add connection string

Create `appsettings.json` in the project root:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=university_db;Username=YOUR_USER;Password=YOUR_PASSWORD"
  }
}
```

Replace `YOUR_USER` and `YOUR_PASSWORD` with your PostgreSQL credentials.


**Important:** Do not commit real passwords to version control. Use User Secrets for local development:

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Port=5432;Database=university_db;Username=postgres;Password=yourpass"
```

Then read the connection string from User Secrets or `appsettings.json` in your code.

---

## Part D — Program.cs: interactive console with menu

Copy the following complete `Program.cs` into your project. It provides an **interactive menu** so the user can choose which query to run. Each menu option has a **TODO** placeholder—implement the query logic for D1–D8.

**Full Program.cs to copy:**

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using UniversityConsole.Data;
using UniversityConsole.Entities;

// --- Setup (already complete) ---
var configuration = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false)
    .Build();

var connectionString = configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

var options = new DbContextOptionsBuilder<UniversityDbContext>()
    .UseNpgsql(connectionString)
    .Options;

await RunAsync();

async Task RunAsync()
{
    await using var context = new UniversityDbContext(options);

    while (true)
    {
        Console.WriteLine("\n=== University Database Console ===");
        Console.WriteLine("1. List all students");
        Console.WriteLine("2. List courses with teachers");
        Console.WriteLine("3. List grades for a student");
        Console.WriteLine("4. List enrollments for a course");
        Console.WriteLine("5. List all teachers");
        Console.WriteLine("6. Create new student (TODO)");
        Console.WriteLine("7. Update student (TODO)");
        Console.WriteLine("8. Delete student (TODO)");
        Console.WriteLine("9. Re-seed database");
        Console.WriteLine("0. Exit");
        Console.Write("\nChoice: ");
        var input = Console.ReadLine()?.Trim();

        if (input == "0") break;

        switch (input)
        {
            case "1":
                // ========== TODO D1: List all students ==========
                Console.WriteLine("(D1 not yet implemented)");
                break;

            case "2":
                // ========== TODO D2: List courses with teacher names ==========
                Console.WriteLine("(D2 not yet implemented)");
                break;

            case "3":
                Console.Write("Student ID: ");
                if (int.TryParse(Console.ReadLine(), out var studentId))
                {
                    // ========== TODO D3: List a student's grades ==========
                    Console.WriteLine("(D3 not yet implemented)");
                }
                else Console.WriteLine("Invalid ID.");
                break;

            case "4":
                Console.Write("Course ID: ");
                if (int.TryParse(Console.ReadLine(), out var courseId))
                {
                    // ========== TODO D4: List enrollments for a course ==========
                    Console.WriteLine("(D4 not yet implemented)");
                }
                else Console.WriteLine("Invalid ID.");
                break;

            case "5":
                // ========== TODO D5: List all teachers ==========
                Console.WriteLine("(D5 not yet implemented)");
                break;

            case "6":
                // ========== (Optional) TODO D6: Create new student ==========
                Console.WriteLine("(D6 not yet implemented)");
                break;

            case "7":
                // ========== (Optional) TODO D7: Update student ==========
                Console.WriteLine("(D7 not yet implemented)");
                break;

            case "8":
                // ========== (Optional) TODO D8: Delete student ==========
                Console.WriteLine("(D8 not yet implemented)");
                break;

            case "9":
                await SeedDatabaseAsync(context);
                break;

            default:
                Console.WriteLine("Invalid choice.");
                break;
        }
    }

    Console.WriteLine("\nGoodbye.");
}

// Re-seed helper method in case you need to reset the table content
// This doesn't rebuild the database
async Task SeedDatabaseAsync(UniversityDbContext context)
{
    Console.Write("This will delete all data and re-insert seed data. Continue? (y/N): ");
    if (Console.ReadLine()?.Trim().ToLowerInvariant() != "y") return;

    await context.Database.ExecuteSqlRawAsync(@"
        TRUNCATE TABLE grades, enrollments, courses, students, teachers
        RESTART IDENTITY CASCADE");

    context.Teachers.AddRange(
        new Teacher { FullName = "Liisa Korhonen", Email = "liisa@uni.fi" },
        new Teacher { FullName = "Pekka Salo", Email = "pekka@uni.fi" },
        new Teacher { FullName = "Maria Lind", Email = "maria@uni.fi" });
    await context.SaveChangesAsync();

    context.Students.AddRange(
        new Student { FullName = "Aino Laine", Email = "aino@uni.fi" },
        new Student { FullName = "Mika Virtanen", Email = "mika@uni.fi" },
        new Student { FullName = "Sara Niemi", Email = null },
        new Student { FullName = "Olli Koski", Email = "olli@gmail.com" });
    await context.SaveChangesAsync();

    var teachers = await context.Teachers.OrderBy(t => t.TeacherId).ToListAsync();
    var students = await context.Students.OrderBy(s => s.StudentId).ToListAsync();
    context.Courses.AddRange(
        new Course { Title = "Databases", Credits = 5, TeacherId = teachers[0].TeacherId },
        new Course { Title = "Algorithms", Credits = 6, TeacherId = teachers[1].TeacherId },
        new Course { Title = "Web Development", Credits = 5, TeacherId = teachers[2].TeacherId });
    await context.SaveChangesAsync();

    var courses = await context.Courses.OrderBy(c => c.CourseId).ToListAsync();
    context.Enrollments.AddRange(
        new Enrollment { StudentId = students[0].StudentId, CourseId = courses[0].CourseId },
        new Enrollment { StudentId = students[0].StudentId, CourseId = courses[1].CourseId },
        new Enrollment { StudentId = students[1].StudentId, CourseId = courses[0].CourseId },
        new Enrollment { StudentId = students[2].StudentId, CourseId = courses[0].CourseId },
        new Enrollment { StudentId = students[2].StudentId, CourseId = courses[2].CourseId },
        new Enrollment { StudentId = students[3].StudentId, CourseId = courses[2].CourseId });
    await context.SaveChangesAsync();

    context.Grades.AddRange(
        new Grade { StudentId = students[0].StudentId, CourseId = courses[0].CourseId, GradeValue = 5 },
        new Grade { StudentId = students[0].StudentId, CourseId = courses[1].CourseId, GradeValue = 4 },
        new Grade { StudentId = students[1].StudentId, CourseId = courses[0].CourseId, GradeValue = 3 },
        new Grade { StudentId = students[2].StudentId, CourseId = courses[0].CourseId, GradeValue = 2 },
        new Grade { StudentId = students[2].StudentId, CourseId = courses[2].CourseId, GradeValue = 5 },
        new Grade { StudentId = students[3].StudentId, CourseId = courses[2].CourseId, GradeValue = 4 });
    await context.SaveChangesAsync();

    Console.WriteLine("Database re-seeded successfully.");
}
```

---

## Part E — Verification

1. Run the application: `dotnet run`
2. Use the menu: choose 1–9. For 3 and 4, enter a valid student or course ID (e.g., 1). Use 9 to re-seed after testing Create/Update/Delete.
3. Choose 0 to exit.
4. Verify that the output matches the data in the database (e.g., via psql or pgAdmin).

---

## Optional extensions

- For D8: before deleting, check if the student has enrollments or grades; optionally delete those first, or show a message that the student cannot be deleted.
- Add basic error handling: if a student or course ID is not found, display a friendly message.
- After showing results, add `Console.WriteLine("Press Enter to continue..."); Console.ReadLine();` so the user can read the output before the menu reappears.

---

## Checklist

- [ ] Console project created with EF Core and Npgsql
- [ ] All five entities defined and mapped to existing schema
- [ ] Composite keys configured for Enrollment and Grade
- [ ] DbContext created and connection string loaded from configuration
- [ ] Interactive menu runs; at least three read options (D1–D5) implemented
- [ ] Options 3 and 4 prompt for IDs and display correct data from `university_db`
- [ ] (Optional) D6 Create, D7 Update, D8 Delete implemented
- [ ] Option 9 Re-seed works; database can be reset to original seed data

---

## Related materials

- [12 – Databases in Programming](./Materials/12-Databases-in-Programming.md)
- [13 – Entity Framework Core](./Materials/13-ORM-and-EF-Core.md)
- [university_db_schema.sql](./Materials/Example-db/university_db_schema.sql)
- [university_db_seed.sql](./Materials/Example-db/university_db_seed.sql)
