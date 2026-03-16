# Assignment 4 — TrailShop: EF Core Console App and Order Tracking

> [!NOTE]
> This assignment continues from **Assignment 3**. You must have the TrailShop database with all tables (categories, products, customers, orders, order_items, stores, stocks, employees) before starting.

> [!IMPORTANT]
> Copy the Assignment-4 folder with this Instructions.md file into your classroom repository.

Your classroom repository structure should look similar to this:

```md
your-Classroom-repo-name
├── Assignment-1
│ ├── 01_schema.sql
│ ├── 01_seed.sql
│ ├── 01_queries.sql
│ └── Instructions.md
├── Assignment-2
│ ├── 02_schema.sql
│ ├── 02_seed.sql
│ ├── 02_queries.sql
│ └── Instructions.md
├── Assignment-3
│ ├── 03_schema.sql
│ ├── 03_seed.sql
│ ├── 03_indexes.sql
│ ├── 03_roles.sql
│ ├── 03_queries.sql
│ └── Instructions.md
├── Assignment-4
│ ├── TrailShopConsole/
│ │ └── (project files)
│ ├── 04_seed_order_tracking.sql
│ └── Instructions.md
└── README.md
```

## Prerequisites

- Completed Assignments 1–3 (TrailShop database)
- .NET 10 SDK
- PostgreSQL with TrailShop database created and populated
- Familiarity with [13-Entity Framework Core](../../Materials/13-Entity-Framework-Core.md), [15-Migrations](../../Materials/15-Entity-Framework-Core-Migrations.md) & [16-Scaffolding](../../Materials/16-Entity-Framework-Core-Scaffolding.md)
- Exercise 5 (University Console with EF Core) is helpful but not required

---

## Scenario

TrailShop wants a **console application** to manage the database and support **order tracking**. You will:

1. Create a .NET console app and **scaffold** the DbContext and entity classes from the existing TrailShop database
2. Create an **initial baseline migration** to establish the current schema in migration history
3. Extend the model and use migrations to add order tracking (`order_status` on orders, new `order_tracking` table)
4. Implement menu options to view orders, update status, and manage tracking history

---

# Part 1 — Create the Console Application

## 1.1 — Project setup

Create a new console application named `TrailShopConsole` inside the Assignment-4 folder:

```bash
dotnet new console -n TrailShopConsole -o TrailShopConsole
cd TrailShopConsole
```

Add EF Core packages:

```bash
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.Extensions.Configuration.Json
```

Install the EF Core CLI tools globally (if not already installed):

```bash
dotnet tool install --global dotnet-ef
```

## 1.2 — Connection string

Create `appsettings.json` in the project root:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=trailshop;Username=YOUR_USER;Password=YOUR_PASSWORD"
  }
}
```

Replace `YOUR_USER`, `YOUR_PASSWORD`, and `trailshop` with your actual database name and credentials.

**Important:** Do not commit real passwords to version control. Use User Secrets for local development:

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Port=5432;Database=trailshop;Username=postgres;Password=yourpass"
```

---

# Part 2 — Scaffold DbContext and Entities from Database

Use EF Core’s **scaffolding** to generate the DbContext and entity classes from your existing TrailShop database.

## 2.1 — Run the scaffold command

From the project directory, run:

```bash
dotnet ef dbcontext scaffold "Host=localhost;Port=5432;Database=trailshop;Username=YOUR_USER;Password=YOUR_PASSWORD" Npgsql.EntityFrameworkCore.PostgreSQL -o Entities -c TrailShopDbContext --context-dir Data --no-onconfiguring
```

Replace the connection string with your actual credentials (or use the same values as in `appsettings.json`). The scaffold command reads directly from the database, so the connection string must be valid.

**Options explained:**

- `-o Entities` — output entity classes to the `Entities` folder
- `-c TrailShopDbContext` — name of the generated DbContext class
- `--context-dir Data` — put the DbContext in the `Data` folder
- `--no-onconfiguring` — do not add `OnConfiguring` with a hardcoded connection string (we will use configuration from `appsettings.json`)

## 2.2 — Add a constructor and design-time support

The scaffolded DbContext may only have a parameterless constructor. Add a constructor that accepts `DbContextOptions` so the app can pass the connection from configuration:

```csharp
public TrailShopDbContext(DbContextOptions<TrailShopDbContext> options)
    : base(options)
{
}
```

**Design-time support for migrations:** The EF Core tools (`dotnet ef migrations add`, `dotnet ef database update`) need to create a `DbContext` instance. With `--no-onconfiguring` and only an options-based constructor, they cannot resolve the options. Add a design-time factory so migrations work.

Create `Data/TrailShopDbContextFactory.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;

namespace TrailShopConsole.Data;

public class TrailShopDbContextFactory : IDesignTimeDbContextFactory<TrailShopDbContext>
{
    public TrailShopDbContext CreateDbContext(string[] args)
    {
        var configuration = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: false)
            .Build();

        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

        var optionsBuilder = new DbContextOptionsBuilder<TrailShopDbContext>();
        optionsBuilder.UseNpgsql(connectionString);

        return new TrailShopDbContext(optionsBuilder.Options);
    }
}
```

Adjust the namespace if needed. The EF Core tools will use this factory when running migrations. Ensure `Program.cs` builds the options from the connection string for runtime (see Part 6 and [Exercise 5](../../Exercises/Exercise-5/Instructions.md)).

## 2.3 — What gets generated

Scaffolding creates entities for all tables in the database: `Category`, `Product`, `Customer`, `Order`, `OrderItem`, `Store`, `Stock`, `Employee`. At this point, the `orders` table does **not** have `order_status`, and there is no `order_tracking` table. You will add those in Part 4 and Part 5.

**Note:** After you modify the scaffolded files in Part 4, do not re-run the scaffold command, or your changes will be overwritten.

## 2.4 — Test that scaffolding was successful

Replace the contents of `Program.cs` with the template below. It uses the same interactive menu structure as [Exercise 5](../../Exercises/Exercise-5/Instructions.md). Options 1 and 2 run simple queries; if they work, the scaffolding was successful.

**Adjust the namespace** in the `using` statement if your scaffolded DbContext uses a different namespace (e.g. `TrailShopConsole.Data` or `TrailShopConsole`). Adjust `Categories` and `Products` if your scaffolded DbContext uses different `DbSet` property names.

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using TrailShopConsole.Data;  // Adjust namespace to match your scaffolded DbContext

// --- Setup (already complete) ---
var configuration = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false)
    .Build();

var connectionString = configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

var options = new DbContextOptionsBuilder<TrailShopDbContext>()
    .UseNpgsql(connectionString)
    .Options;

await RunAsync();

async Task RunAsync()
{
    await using var context = new TrailShopDbContext(options);

    while (true)
    {
        Console.WriteLine("\n=== TrailShop Database Console ===");
        Console.WriteLine("1. List categories");
        Console.WriteLine("2. List products (first 5)");
        Console.WriteLine("0. Exit");
        Console.Write("\nChoice: ");
        var input = Console.ReadLine()?.Trim();

        if (input == "0") break;

        switch (input)
        {
            case "1":
                var categories = await context.Categories.OrderBy(c => c.CategoryId).ToListAsync();
                Console.WriteLine($"\nCategories ({categories.Count}):");
                foreach (var c in categories)
                    Console.WriteLine($"  {c.CategoryId}: {c.Name}");
                break;

            case "2":
                var products = await context.Products.OrderBy(p => p.ProductId).Take(5).ToListAsync();
                var total = await context.Products.CountAsync();
                Console.WriteLine($"\nProducts (first 5 of {total}):");
                foreach (var p in products)
                    Console.WriteLine($"  {p.ProductId}: {p.Name} ({p.Price:C})");
                break;

            default:
                Console.WriteLine("Invalid choice.");
                break;
        }
    }

    Console.WriteLine("\nGoodbye.");
}
```

Run the application:

```bash
dotnet run
```

You should see categories and products from your TrailShop database. If you get errors about missing namespaces or properties, check that the scaffold completed and that the `using` directive and `DbSet` names match your generated code. Once this works, proceed to Part 3.

---

# Part 3 — Create Initial Baseline Migration

Create a **baseline migration** that records the current schema in EF Core’s migration history without changing the database. This lets later migrations only apply new changes. Do this **before** adding `order_status` and `order_tracking`.

## 3.1 — Create the baseline migration

From the project directory:

```bash
dotnet ef migrations add InitialCreate
```

This generates a migration whose `Up` method would create all existing tables. Because those tables already exist, we make this migration a no-op.

## 3.2 — Edit the baseline to a no-op

Open the generated `Migrations/[timestamp]_InitialCreate.cs` file. In the `Up` method, remove all statements so it is empty:

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    // No-op: tables already exist from Assignments 1-3
}
```

Leave the `Down` method as is (or empty it as well if you prefer). The baseline only needs to be recorded in history; it should not alter the database.

## 3.3 — Apply the baseline

```bash
dotnet ef database update
```

This adds the `InitialCreate` migration to `__EFMigrationsHistory` and runs the empty `Up` method, so no schema changes occur. EF Core now treats this as the starting point for future migrations. Proceed to Part 4.

---

# Part 4 — Extend the Model for Order Tracking

Add support for order tracking to the scaffolded model. The database does not have these yet; the migration in Part 5 will create them. Use the **Fluent API** in the DbContext to configure mapping (no data annotations on the entities).

## 4.1 — Add order_status to the Order entity

Open `Entities/Order.cs` (or the scaffolded name) and add a simple property:

```csharp
public string OrderStatus { get; set; } = "PENDING";
```

Add a navigation collection for tracking history:

```csharp
public ICollection<OrderTracking> OrderTrackings { get; set; } = new List<OrderTracking>();
```

Map the property to the database in the DbContext with the Fluent API (see 4.3). Allowed values: `PENDING`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`.

## 4.2 — Create the OrderTracking entity

Create a new file `Entities/OrderTracking.cs` with a plain class (no attributes). All table and column mapping will be done in the DbContext:

```csharp
namespace TrailShopConsole.Entities;

public class OrderTracking
{
    public int TrackingId { get; set; }
    public int OrderId { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime RecordedAt { get; set; }
    public string? Notes { get; set; }

    public Order Order { get; set; } = null!;
}
```

**Adjust the namespace** to match your scaffolded entities (e.g. `TrailShopConsole.Entities` or whatever the scaffold generated).

## 4.3 — Configure with Fluent API in DbContext

In `Data/TrailShopDbContext.cs`:

1. Add `DbSet<OrderTracking> OrderTrackings => Set<OrderTracking>();`

2. In `OnModelCreating`, add Fluent API configuration for both entities:

**Order — map OrderStatus:**

```csharp
modelBuilder.Entity<Order>(entity =>
{
    entity.Property(o => o.OrderStatus)
        .HasColumnName("order_status")
        .HasMaxLength(20)
        .HasDefaultValue("PENDING");
});
```

> If the scaffolded `Order` entity is already configured in `OnModelCreating`, add the `OrderStatus` property configuration to that existing `Order` block instead of creating a new one.

**OrderTracking — table, columns, key, and relationship:**

```csharp
modelBuilder.Entity<OrderTracking>(entity =>
{
    entity.ToTable("order_tracking");

    entity.HasKey(e => e.TrackingId);

    entity.Property(e => e.TrackingId)
        .HasColumnName("tracking_id")
        .UseIdentityByDefaultColumn();

    entity.Property(e => e.OrderId).HasColumnName("order_id");
    entity.Property(e => e.Status).HasColumnName("status").HasMaxLength(20);
    entity.Property(e => e.RecordedAt).HasColumnName("recorded_at");
    entity.Property(e => e.Notes).HasColumnName("notes");

    entity.HasOne(e => e.Order)
        .WithMany(o => o.OrderTrackings)
        .HasForeignKey(e => e.OrderId)
        .OnDelete(DeleteBehavior.Cascade);
});
```

---

# Part 5 — EF Core Migration for Order Tracking

Because you created a baseline migration in Part 3, EF Core now knows the existing schema. The next migration will contain only the new changes.

## 5.1 — Create the migration

From the project directory:

```bash
dotnet ef migrations add AddOrderTracking
```

This generates a migration that should add only the `order_status` column and the `order_tracking` table. Open the generated file and verify that the `Up` method contains:

- `AddColumn` (or similar) for `order_status` on the `orders` table
- `CreateTable` for `order_tracking`

If the migration incorrectly includes `CreateTable` for existing tables (`categories`, `products`, etc.), remove those and keep only the `order_status` and `order_tracking` changes. With the baseline applied correctly, this should not be necessary.

## 5.2 — Apply the migration

```bash
dotnet ef database update
```

This updates the database and records the migration in `__EFMigrationsHistory`. Existing data is preserved; existing orders get `order_status = 'PENDING'` by default.

## 5.3 — Seed order tracking data

Insert initial tracking history so you have data to test the "View order tracking history" and "Update order status" features.

Create `04_seed_order_tracking.sql` in the Assignment-4 folder:

```sql
-- Seed order tracking history for existing orders
-- Run this after applying the AddOrderTracking migration (e.g. via psql or pgAdmin)

-- Order 1: Full tracking history (PENDING -> CONFIRMED -> SHIPPED)
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (1, 'PENDING', '2024-01-15 10:00:00', 'Order placed'),
  (1, 'CONFIRMED', '2024-01-16 09:00:00', 'Payment received'),
  (1, 'SHIPPED', '2024-01-18 14:30:00', 'Dispatched via standard delivery');

UPDATE orders SET order_status = 'SHIPPED' WHERE order_id = 1;

-- Order 2: PENDING -> CONFIRMED
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (2, 'PENDING', '2024-02-20 11:15:00', 'Order placed'),
  (2, 'CONFIRMED', '2024-02-21 08:00:00', 'Processing');

UPDATE orders SET order_status = 'CONFIRMED' WHERE order_id = 2;

-- Orders 3, 4, 5: Initial PENDING only
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (3, 'PENDING', '2024-01-22 16:45:00', 'Order placed'),
  (4, 'PENDING', '2024-02-10 09:30:00', 'Order placed'),
  (5, 'PENDING', '2024-03-01 13:00:00', 'Order placed');
```

Run the script against your TrailShop database (e.g. `psql -d trailshop -f 04_seed_order_tracking.sql` or execute it in pgAdmin). This gives you sample tracking history: order 1 has three entries, order 2 has two, and orders 3–5 each have one.

---

# Part 6 — Program.cs Menu

Implement an interactive menu in `Program.cs` with at least these options:

1. **List all orders** — Show order_id, order_date, customer full_name, order_status. Order by order_date descending.
2. **List order details** — Prompt for order_id; show order header (customer, date, status) and order items (product name, quantity, unit_price).
3. **View order tracking history** — Prompt for order_id; show all tracking entries (status, recorded_at, notes) for that order, ordered by recorded_at.
4. **Update order status** — Prompt for order_id and new status. Update `orders.order_status` and insert a new row into `order_tracking` with the new status and current timestamp.
5. **List customers** — Show customer_id, full_name, email.
6. **List products by category** — Show products with their category name.
7. **Exit**

Use the same configuration and DbContext setup pattern as in Exercise 5 (read connection string from configuration, create options, run menu loop).

---

# Submission Requirements

Submit in the Assignment-4 folder:

- `TrailShopConsole/` — the full .NET project (Program.cs, Entities, Data, Migrations, appsettings.json, .csproj)
- `04_seed_order_tracking.sql` — seed data for order tracking (run after migration)

Your classroom repository should look like:

```md
Assignment-4
├── TrailShopConsole/
│ ├── Entities/
│ │ ├── Category.cs (scaffolded)
│ │ ├── Product.cs (scaffolded)
│ │ ├── Customer.cs (scaffolded)
│ │ ├── Order.cs (scaffolded, then modified with OrderStatus)
│ │ ├── OrderItem.cs (scaffolded)
│ │ ├── Store.cs (scaffolded)
│ │ ├── Stock.cs (scaffolded)
│ │ ├── Employee.cs (scaffolded)
│ │ └── OrderTracking.cs (created manually)
│ ├── Data/
│ │ ├── TrailShopDbContext.cs (scaffolded, then modified)
│ │ └── TrailShopDbContextFactory.cs (design-time support for migrations)
│ ├── Migrations/
│ │ ├── [timestamp]\_InitialCreate.cs
│ │ ├── [timestamp]\_AddOrderTracking.cs
│ │ └── TrailShopDbContextModelSnapshot.cs
│ ├── Program.cs
│ ├── appsettings.json
│ └── TrailShopConsole.csproj
├── 04_seed_order_tracking.sql
└── Instructions.md
```

Scaffolding may generate slightly different names or namespaces depending on your database; adjust namespaces in `OrderTracking.cs` to match.

---

# Self-check

Before submitting, verify:

1. Does the scaffold command complete and generate entity classes and DbContext?
2. Does the baseline migration (InitialCreate) apply without errors?
3. Does the AddOrderTracking migration apply without errors?
4. Does the app connect to TrailShop and run without errors?
5. Did you run `04_seed_order_tracking.sql` after the migration?
6. Does option 1 list all orders with customer names and status?
7. Does option 3 show tracking history (e.g. order 1 has 3 entries, order 2 has 2)?
8. When you update an order status (option 4), is a new row inserted into `order_tracking`?

---

# Related materials

- [Materials 13 — Entity Framework Core](../../Materials/13-Entity-Framework-Core.md)
- [Exercise 5 — University Console with EF Core](../../Exercises/Exercise-5/Instructions.md)
- [Assignment 1–3 schema and seed files](../Assignment-1/), [Assignment-2](../Assignment-2/), [Assignment-3](../Assignment-3/))
