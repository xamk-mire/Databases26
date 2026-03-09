# Managing Users and Roles in Programming

### How applications handle authentication, authorization, and database access

This material is a follow-up to [Databases in Programming](12-Databases-in-Programming.md) and [Users and Roles](11-Users-and-Roles.md). 

## 1) Two Levels of "Users" and "Roles"

### Application users vs database users

It is easy to confuse two different concepts:

| Concept | What it is | Where it lives | Who uses it |
|---------|------------|----------------|-------------|
| **Application users** | People (or systems) who use your app—e.g., Alice, Bob, "admin@company.com" | Rows in your app's `Users` table (or similar) | Your application code, after login |
| **Database users/roles** | Identities used to **connect** to the database (e.g., `app_user`, `app_read`) | Database system catalogs (PostgreSQL `pg_roles`, etc.) | Database driver, connection string |

In most web applications:

- **End users** (Alice, Bob) are stored as rows in a `Users` table. They log in with email/password. The app verifies credentials and creates a session.
- The **application** connects to the database as a single **database user** (e.g., `app_user` or `uni_write`). All queries run under that identity. Alice and Bob do **not** have their own database logins.

```
┌─────────────────────────────────────────────────────────────────┐
│  Alice (application user) ──► logs in ──► session / JWT          │
│  Bob (application user)   ──► logs in ──► session / JWT          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Application connects to database as: app_user (database role)   │
│  All queries (for Alice, Bob, etc.) run as app_user              │
└─────────────────────────────────────────────────────────────────┘
```

Understanding this separation is essential for designing both database access and application security.

---

## 2) How the Application Connects to the Database

### Single database user: the typical pattern

Most applications use **one database user** for all operations:

- The connection string contains credentials for that user (e.g., `app_user` / `password`).
- Every query—whether for Alice, Bob, or an anonymous visitor—runs as that user.
- The database grants that user the privileges it needs (e.g., SELECT, INSERT, UPDATE, DELETE on app tables). See [Materials 11](11-Users-and-Roles.md) for how to set up roles and grants.

### Why not one database user per application user?

Creating a PostgreSQL role for each end user (Alice, Bob, …) would:

- Be hard to manage at scale (thousands of users)
- Conflict with connection pooling (pools assume a small number of distinct identities)
- Require dynamic connection strings, which complicates security and configuration

Instead, the app uses **one** database identity and enforces **who can do what** in application logic (e.g., "only show Alice her own orders").

### When multiple database users make sense

Sometimes you use different database users for **different parts of the system**:

| Scenario | Example |
|----------|---------|
| **Read-only reporting** | A reporting service connects as `app_read` (SELECT only) to reduce blast radius if compromised |
| **Background jobs** | A worker might use `app_write` or a dedicated role with limited privileges |
| **Migrations / admin** | Schema changes run as an admin role; the app runs as `app_user` |
| **Multi-tenant with row-level security** | Advanced setups may use per-tenant roles; this is less common |

For typical CRUD applications, a single app database user is the norm.

---

## 3) Storing Application Users and Roles

### Tables for users and roles

Application users and roles are usually stored in **your own tables**, not in database system catalogs.

A minimal design:

- **Users** — `id`, `email`, `password_hash`, `name`, `created_at`, etc.
- **Roles** — `id`, `name` (e.g., `"Admin"`, `"User"`, `"Moderator"`)
- **UserRoles** — junction table linking users to roles (many-to-many)

```
Users                    UserRoles                 Roles
┌────────────┬─────────┐  ┌──────────┬─────────┐  ┌────────┬──────────┐
│ id         │ email   │  │ user_id  │ role_id │  │ id     │ name     │
├────────────┼─────────┤  ├──────────┼─────────┤  ├────────┼──────────┤
│ 1          │ a@x.com │──│ 1        │ 2       │──│ 1      │ Admin    │
│ 2          │ b@x.com │  │ 1        │ 1       │  │ 2      │ User     │
└────────────┴─────────┘  │ 2        │ 1       │  └────────┴──────────┘
                          └──────────┴─────────┘
```

### Important: never store plaintext passwords

Passwords must be **hashed** (one-way) before storage. Never store plaintext passwords.

- Use a **password hashing algorithm** designed for the purpose: bcrypt, Argon2, or PBKDF2 with a high iteration count.
- At login, hash the provided password and compare it to the stored hash. If they match, the password is correct.
- Do not use fast hashes like MD5 or SHA256 alone for passwords; they are too quick to brute-force.

Most frameworks provide built-in helpers (e.g., ASP.NET Core Identity uses a secure default).

---

## 4) Authentication and Authorization

### Authentication: who are you?

**Authentication** answers: *"Who is this request from?"*

- User submits email and password.
- App looks up the user, verifies the password against the stored hash.
- If valid, the app creates a **session** (cookie) or **token** (e.g., JWT) that identifies the user for subsequent requests.
- Later requests include the session/token; the app knows which user is making the request.

### Authorization: what can you do?

**Authorization** answers: *"Is this user allowed to do this?"*

- After authentication, the app checks whether the user has permission for the action.
- Common approach: **role-based access control (RBAC)**. The user has one or more roles; each role implies a set of permissions.
- Example: only users with the `Admin` role can access `/admin/users`. The app checks the user's roles before allowing access.

### Flow

1. **Request** → includes session cookie or JWT.
2. **Authentication** → resolve user from session/token (or return 401 if invalid).
3. **Authorization** → check if user has required role/permission for this endpoint (or return 403 if not).
4. **Business logic** → execute the action (e.g., load data, apply changes).

---

## 5) Role-Based Access Control in Code

### Checking roles in application logic

Once you know the current user and their roles, you enforce permissions in code.

**Pseudocode (conceptual):**

```
if (currentUser.Roles.Contains("Admin")) {
    // Allow access to admin panel
} else {
    return Forbidden();
}
```

### .NET: ASP.NET Core Identity and authorization

ASP.NET Core provides **Identity** for user/role storage and **authorization** for permission checks.

#### Identity setup (users and roles in the database)

Identity stores users and roles in tables it creates (e.g., `AspNetUsers`, `AspNetRoles`, `AspNetUserRoles`). You configure it to use your database (e.g., via EF Core):

```csharp
// Program.cs
builder.Services.AddDefaultIdentity<IdentityUser>(options => { /* ... */ })
    .AddRoles<IdentityRole>()
    .AddEntityFrameworkStores<ApplicationDbContext>();
```

#### Role-based authorization

Use the `[Authorize]` attribute to require roles:

```csharp
[Authorize(Roles = "Admin")]
public class AdminController : ControllerBase
{
    // Only users with Admin role can reach these actions
}

[Authorize(Roles = "Admin,Moderator")]
public IActionResult EditPost(int id)
{
    // Admin OR Moderator
}
```

#### Policy-based authorization (more flexible)

For complex rules, define policies:

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("RequireAdmin", policy => policy.RequireRole("Admin"));
    options.AddPolicy("CanEditPost", policy =>
        policy.RequireAssertion(context =>
            context.User.IsInRole("Admin") || context.User.IsInRole("Moderator")));
});
```

```csharp
[Authorize(Policy = "RequireAdmin")]
public IActionResult DeleteUser(int id) { /* ... */ }
```

### Other ecosystems

| Platform | Common approach |
|----------|-----------------|
| **Node.js / Express** | Passport.js + custom middleware to check roles |
| **Python / Django** | Django auth (User, Group) + `@login_required`, `@user_passes_test` |
| **Python / Flask** | Flask-Login + Flask-Principal or custom decorators |
| **Java / Spring** | Spring Security with `@PreAuthorize`, `@Secured` |

The pattern is the same: authenticate first, then check roles or permissions before allowing access.

---

## 6) Data Access and the Current User

### Filtering by current user

Often, users may only see or change **their own** data:

- Alice sees only her orders.
- A student sees only their enrollments.

This is enforced in the **query**, not only at the endpoint level:

```csharp
// Conceptual: only return orders for the logged-in user
var userId = User.FindFirstValue(ClaimTypes.NameIdentifier); // or similar
var orders = await context.Orders
    .Where(o => o.UserId == userId)
    .ToListAsync();
```

If you forget this filter, a user might access another user's data by changing the request (e.g., `GET /orders?userId=123`). **Always** scope queries to the current user (or to resources the user is explicitly allowed to access).

### Ownership checks before updates

Before updating or deleting, verify the current user owns the resource:

```csharp
var order = await context.Orders.FindAsync(orderId);
if (order == null) return NotFound();
if (order.UserId != currentUserId) return Forbidden();
// Proceed with update
```

---

## 7) Identity Frameworks and ORM Integration

### Why use an identity framework?

Implementing authentication and authorization from scratch is error-prone. Frameworks provide:

- Password hashing
- Session/token handling
- Role storage and lookup
- Protection against common attacks (CSRF, session fixation, etc.)

### ASP.NET Core Identity with EF Core

Identity integrates with EF Core. The `ApplicationDbContext` includes `DbSet<IdentityUser>`, `DbSet<IdentityRole>`, etc. Migrations create and update the identity tables.

```csharp
public class ApplicationDbContext : IdentityDbContext<IdentityUser>
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options) { }

    public DbSet<Order> Orders { get; set; }
    // Identity adds: Users, Roles, UserRoles, etc.
}
```

You can extend the user model (e.g., add `FullName`) by creating a custom class that inherits from `IdentityUser` and use it in place of `IdentityUser`.

### Custom user/role tables without Identity

If you prefer not to use Identity, you can:

- Define your own `User`, `Role`, and `UserRole` entities.
- Implement password hashing (e.g., via `BCrypt.Net` or similar).
- Implement login and session handling yourself.
- Use the same authorization attributes (`[Authorize]`, policies) with a custom authentication handler that loads the user and roles from your tables.

This gives full control but requires more code and care.

---

## 8) Security Best Practices

### Credentials and configuration

- **Never** hardcode database passwords or API keys in source code.
- Use **environment variables** or a secure configuration store (e.g., Azure Key Vault, AWS Secrets Manager).
- Restrict access to production credentials.

### Database user: least privilege

- The application's database user should have **only** the privileges it needs.
- Prefer read-only connections for reporting or read-heavy services.
- Avoid `SUPERUSER` or schema-altering rights for the normal app user. See [Materials 11](11-Users-and-Roles.md) for role design.

### Application users: defense in depth

- **Authentication** — strong password policy, optional MFA.
- **Authorization** — check roles/permissions on every protected endpoint.
- **Data access** — always filter by `UserId` or equivalent when returning user-specific data.
- **Audit** — log sensitive actions (login, role changes, data exports) for debugging and compliance.

### Common pitfalls

| Pitfall | Safer approach |
|---------|----------------|
| Trusting client-provided user IDs | Derive the current user from the session/token; never from query parameters |
| Skipping authorization on "internal" APIs | Every endpoint that returns or modifies data should check permissions |
| Storing plaintext passwords | Use a proper password hashing library |
| Overprivileged database user | Create a dedicated role with minimal grants |

---

## 9) Summary

| Topic | Key idea |
|-------|----------|
| **Application users vs database users** | App users (Alice, Bob) live in your tables; the app connects to the DB as one database user |
| **Connection pattern** | Typically one database user; multiple DB users for different services (e.g., read-only) when needed |
| **User and role storage** | Store users and roles in your own tables (or use Identity); never store plaintext passwords |
| **Authentication** | Verify identity (e.g., email/password); create session or token |
| **Authorization** | Check roles/permissions before allowing access; use `[Authorize]`, policies, or equivalent |
| **Data scoping** | Filter queries by current user; verify ownership before updates/deletes |
| **Identity frameworks** | Use ASP.NET Core Identity (or similar) to avoid reinventing auth |
| **Security** | Least privilege for DB user; no hardcoded secrets; defense in depth |

---

## Related materials

- [11 – Users and Roles](11-Users-and-Roles.md) — Database-level roles, privileges, GRANT/REVOKE in PostgreSQL
- [12 – Databases in Programming](12-Databases-in-Programming.md) — Purpose of databases in programming, connection patterns
- [13 – Entity Framework Core](13-ORM-and-EF-Core.md) — ORM for .NET, including Identity integration
