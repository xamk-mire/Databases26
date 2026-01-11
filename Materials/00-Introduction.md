### What is Database

A **database** is a **managed collection of persistent data** plus the **mechanisms and rules** for storing it, retrieving it, and keeping it correct and secure under real-world conditions (concurrency, failures, growth).

Put another way: a database is *data + a contract*. (rules for how users can access the stored/existing data)

That “contract” usually includes:

* **A data model** (tables, documents, graph, etc.)
* **A query interface** (SQL, APIs, search queries)
* **Integrity rules** (constraints, validation, relationships)
* **Concurrency control** (so many users can read/write safely)
* **Durability and recovery** (so commits survive crashes)
* **Security and governance** (access control, auditing, encryption)
* **Operational features** (backup/restore, replication, monitoring)

**Example:**
A relational database storing `Customers` and `Orders` isn’t just files with rows — it enforces foreign keys, supports queries like “revenue by month,” and can recover to a consistent state after power loss.

---

### What is Data?

In databases, **data** is *recorded representations of facts or observations*—stored in a structured form so a system can **retrieve, validate, relate, and process** them reliably.

A slightly more “database-native” way to say it:

**Data** is the **persisted symbols** (numbers, text, timestamps, IDs, etc.) that a database manages as **values inside a data model** (tables, documents, graphs), where those values gain meaning through:

* **Schema/structure** (e.g., a column named `birth_date` is expected to be a date)
* **Constraints** (e.g., `order_total >= 0`, foreign keys)
* **Relationships** (e.g., `orders.customer_id → customers.id`)
* **Context/metadata** (units, encoding, timezone, provenance)

#### Quick examples

* `42` is just a value. In a database it becomes data when it’s placed in context:

  * `customers.id = 42` (an identifier)
  * `age = 42` (a measurement with units/meaning)
  * `invoice_total = 42.00` (a currency amount)

* A row like:

  * `Orders(id=1001, customer_id=42, total=59.90, created_at="2026-01-05T10:12:00Z")`
    is data because it captures facts (an order happened) in a structured, queryable form.

#### Helpful distinction (common in DB discussions)

* **Data:** stored representations (the “symbols”).
* **Information:** data interpreted in context (e.g., “customer 42 spent €59.90 today”).
* **Knowledge:** generalized conclusions derived from information (e.g., “customers in segment X tend to buy weekly”).


---

### Metadata??

**Metadata** is **data about data**: information that describes what stored data *means*, how it is *structured*, where it came from, and how it should be *handled*.

In database terms, metadata answers questions like:

* *What is this field?* (name, type, units, allowed values)
* *How is this data organized?* (tables/collections, indexes, partitions)
* *How is it related?* (keys, relationships)
* *Where did it come from?* (source system, ingestion time, lineage)
* *How should it be used?* (permissions, retention, sensitivity classification)

#### Examples of metadata

**Schema metadata (structure)**

* Table: `Orders`
* Column: `created_at TIMESTAMP NOT NULL`
* Constraint: `total >= 0`
* Relationship: `orders.customer_id → customers.id`

**Operational metadata (how it’s stored/served)**

* Index: `idx_orders_created_at`
* Partitioning: “Orders partitioned by month”
* Replication: “3 replicas, one leader”
* Statistics: row counts, value distributions (used by the query optimizer)

**Governance metadata (how it’s controlled)**

* Access rules: “Only finance role can read `salary`”
* Classification: “PII” / “confidential”
* Retention: “Keep logs for 90 days”

**Provenance/lineage metadata (where it came from)**

* “This column is sourced from Salesforce nightly export”
* “This table is produced by job X at 02:00”

---

### Data vs. Metadata

* **Data:** `total = 59.90`
* **Metadata:** `total` is a decimal currency amount in EUR, non-negative, stored in `Orders.total`, indexed for reporting, accessible to roles A/B, retained for 7 years.

---

## Why databases were developed

Before databases, many systems used **files** (flat files, ISAM, bespoke binary formats). This quickly runs into recurring problems:

1. **Data duplication and inconsistency**  
    The same customer exists in multiple files; one update is missed; reality splits.
    
2. **Hard-coded access patterns**  
    If the file layout was designed for “lookup by customer ID,” a new need like “top customers by spend last quarter” becomes painful or impossible without rewriting everything.
    
3. **Concurrency and correctness**  
    Two people editing the same record at the same time creates races, corruption, lost updates.
    
4. **Recovery after failure**  
    Power loss mid-write can leave data half-updated. You need logs, atomicity, crash recovery.
    
5. **Security and auditing**  
    Files don’t naturally provide fine-grained access control, encryption at rest, audit logs.
    
6. **Scaling and performance**  
    As data grows, you need indexes, caching strategies, partitioning, replication, query planning.
    

Databases emerged to **centralize data management** as a dedicated discipline with reusable guarantees—so every application team doesn’t reinvent fragile storage and query logic.

---

## A brief history of databases 


### 1) File-based data management (1950s–1960s)

**What it was:** Data stored in flat files or custom binary formats. Each application “owned” its files and knew exactly how to read/write them.  

**Why it existed:** Disks were expensive, compute was limited, and most programs had narrow requirements.  

**Why it broke down:**

- Every new report required new code.
    
- Data duplication and inconsistency were common.
    
- Concurrency and crash recovery were mostly ad-hoc (often unsafe).
    

**Notable pattern:** _ISAM_ (Indexed Sequential Access Method) and similar approaches: good performance for certain access paths, inflexible for new ones.

---

### 2) Hierarchical databases (1960s–1970s)

**What it was:** Data modeled as a **tree** (parent → child).  

**Why it helped:** If your world is naturally hierarchical (e.g., “company → departments → employees”), you get predictable, fast navigation.  

**Limits:** Many-to-many relationships are awkward (e.g., “students ↔ courses”). Queries tend to be “walk the tree,” which ties the app to the data structure.

---

### 3) Network / CODASYL databases (late 1960s–1970s)

**What it was:** Data modeled as records connected by **explicit links/pointers** (a graph-like structure).  

**Why it helped:** More flexible than trees; many-to-many relationships were representable.  

**Limits:** Still _navigational_: applications traverse predefined paths. If the question changes, code changes. The physical representation leaks into application logic.

---

### 4) The relational model + SQL (1970s–1980s)

**Big shift:** Move from “tell me how to navigate to the data” to “tell me what data you want.”  
**Key ideas:**

- Data as **relations (tables)**
    
- **Declarative querying** (SQL)
    
- **Physical data independence**: the system can change indexes/storage without changing queries
    
- **Constraints** (keys, foreign keys, checks)
    
- **Transactions** and recovery built in
    

**Why relational won:** It made databases _general-purpose_, allowed _ad-hoc queries_, and enabled optimizers to pick efficient plans automatically.

#### Declarative query

You specify the desired result, not the step-by-step procedure.  
Opposite: navigational/procedural access, where you explicitly traverse pointers or loops.

#### SQL (Structured Query Language)

A **declarative** language for querying and manipulating relational data. You describe _what_ you want, and the database decides _how_ to execute it efficiently.

#### Index

A data structure that speeds up lookups (like a book’s index).  
Common types:

- **B-tree**: great for range queries and general-purpose OLTP
    
- **LSM-tree**: great for high write throughput (common in many distributed/NoSQL systems)
    
- **Inverted index**: used for full-text search
    
- **Vector index**: used for nearest-neighbor similarity search
    

#### Transaction

A logical unit of work (e.g., “transfer money from A to B”) that should be correct even if failures occur or many users act simultaneously.


#### Ad-hoc querying

Asking **new questions on the fly** without having pre-built code paths or reports.  
Example: “Show me customers in Helsinki who bought product X in the last 30 days and have churn risk > 0.7.”  
Relational databases made this practical via SQL + query optimization.


---

### 5) Transaction processing becomes central (1980s–1990s)

As databases became the heart of business systems, vendors and researchers focused on:

- High concurrency (many simultaneous users)
    
- Isolation and correctness under contention
    
- Logging and recovery
    
- Better indexing and query planning
    

This is the era where “database = reliable system of record” really solidified.

#### Concurrency control

Mechanisms that keep transactions correct when many run at once. Common approaches:

- **Locking** (block conflicting operations)
    
- **MVCC** (Multi-Version Concurrency Control): readers see a consistent snapshot while writers create new versions.
    

#### Query optimizer / query planning

The database component that chooses _how_ to execute a query (join order, index usage, parallelism). This is one of the reasons declarative SQL can be fast.

---

### 6) Data warehouses and OLAP (1990s–2000s)

Organizations wanted analytics over huge historical datasets: “What were sales by region over 5 years?”  
This differs from operational workloads (placing orders, updating accounts).

**Warehouse/OLAP design trends:**

- Data copied from operational systems into analytical stores (ETL/ELT)
    
- Schema designs like star/snowflake
    
- Heavy use of aggregation, scans, and joins over large datasets
    
- Movement toward **columnar storage** for speed in analytics
    

#### OLAP (Online Analytical Processing)

Workloads focused on **large scans and aggregations** across lots of data.  
Examples: dashboards, trend analysis, cohort analysis, “sales by region over 5 years.”

#### Data warehouse

A system optimized for OLAP, often containing cleaned/combined historical data from multiple sources. Typically the “single place” for analytics.

#### Columnar storage

Data stored **by column** rather than by row.  
Great for OLAP because queries often read a few columns over many rows and aggregate them; also compresses well.

---

### 7) Web scale + NoSQL (mid-2000s–2010s)

Web-scale systems (massive traffic, distributed deployments) exposed limits of traditional “scale-up” relational approaches:

- Needed easier horizontal scaling, high availability, flexible schemas
    
- Many systems traded strict consistency for availability/latency in distributed settings
    

NoSQL isn’t one thing; it’s a family of models (key-value, document, wide-column, graph), each optimizing different access patterns.

#### Horizontal scaling (scale out)

Increasing capacity by **adding more machines** (nodes) and distributing data/work across them.

#### Vertical scaling (scale up)

Increasing capacity by **making one machine bigger** (more CPU/RAM/faster disk).

---

### 8) Distributed SQL / “NewSQL” (2010s–present)

A counter-movement: “We want **SQL + ACID**, but also **horizontal scaling** and multi-region resilience.”  
Modern distributed SQL systems try to keep the relational model and transactional guarantees while distributing storage/compute across nodes.

#### ACID

A set of guarantees for **transactions** (a transaction is a bundle of reads/writes treated as a single unit).

- **Atomicity:** All-or-nothing. If part fails, none of it “half happens.”
    
- **Consistency:** The database enforces rules/constraints so transactions move the DB from one valid state to another.
    
- **Isolation:** Concurrent transactions don’t interfere in ways that create anomalies (appears “as if” some serial order happened, depending on isolation level).
    
- **Durability:** Once committed, changes survive crashes/power loss (via logging, replication, etc.).
    

#### Isolation levels

Different “strengths” of isolation (trade correctness vs performance).  
Examples: read committed, repeatable read, snapshot isolation, serializable.



---

### 9) Specialization explosion (2010s–present)

As infrastructure matured (cloud, cheap storage, orchestration), it became easier to run multiple specialized data systems:

- Time-series databases for observability/IoT
    
- Search engines for full text + filtering
    
- Stream processors / event stores
    
- Vector databases for embedding similarity (AI workloads)
    

Modern architectures often use **polyglot persistence**: different databases for different needs, connected by pipelines.

---

## Database types you see today 

### 1) Relational databases (RDBMS)

**Model:** tables + relations  

**Strengths:** strong integrity, ACID transactions, SQL, mature tooling  

**Best for:** business systems, financials, orders, inventory, anything needing correctness and constraints

Key features:

- Schema, normalization, constraints
    
- Transactions, locks or MVCC
    
- Query planner/optimizer
    
- Secondary indexes
    

### 2) Distributed SQL (often grouped as “NewSQL”)

**Model:** relational + SQL  

**Strengths:** horizontal scale + ACID + familiar SQL  

**Best for:** global apps needing strong correctness with multi-region resilience

Tradeoffs:

- More complex operations
    
- Higher write latency in some configurations due to consensus/replication
    

### 3) Key-value stores

**Model:** key → opaque value  

**Strengths:** very fast simple operations, easy scaling  

**Best for:** caching, session storage, counters, feature flags, simple lookups

Tradeoff:

- Limited query expressiveness unless augmented with secondary indexing modules/features
    

### 4) Document databases

**Model:** documents (often JSON/BSON)  

**Strengths:** flexible schema, natural for application objects, nested data  

**Best for:** content systems, catalogs, event records, rapidly evolving product features

Tradeoffs:

- Joins and cross-document constraints are often weaker than relational
    
- Data duplication can creep in if not designed carefully
    

### 5) Wide-column / column-family stores

**Model:** rows with potentially huge, sparse columns grouped into families  

**Strengths:** high write throughput, large-scale distributed storage, predictable access patterns  

**Best for:** massive logs, telemetry, large sparse datasets, big distributed workloads

Tradeoffs:

- You model queries first; flexibility is lower than relational
    
- Transactions and ad-hoc querying vary by system
    

### 6) Graph databases

**Model:** nodes + edges + properties  

**Strengths:** relationship traversal, path queries, recommendations, network analysis  

**Best for:** social graphs, fraud rings, knowledge graphs, dependency maps

Tradeoffs:

- Some graph queries can be expensive at scale without careful modeling
    
- Often paired with other stores for non-graph workloads
    

### 7) Time-series databases

**Model:** measurements over time (timestamp + tags + values)  

**Strengths:** compression, downsampling, retention policies, fast aggregates over time windows  

**Best for:** metrics, observability, IoT, finance ticks

Tradeoffs:

- Not ideal for highly relational business data
    

### 8) Columnar analytical databases (OLAP)

**Model:** often relational-ish but stored column-wise  

**Strengths:** extremely fast scans/aggregations, compression, vectorized execution  

**Best for:** BI, analytics, dashboards over large datasets, data warehouses/lakes

Tradeoffs:

- Not optimized for high-frequency small transactional updates
    

### 9) Search engines as databases (full-text + relevance)

**Model:** inverted index + documents  

**Strengths:** full-text search, ranking, fuzziness, facets/filters  

**Best for:** site search, logs exploration, document retrieval, observability search

Tradeoffs:

- Not a substitute for transactional truth; often “derived” from source-of-truth data
    

### 10) In-memory databases

**Model:** varies (often key-value or relational) but primary storage is RAM  

**Strengths:** very low latency  

**Best for:** caching, real-time leaderboards, ephemeral state, sometimes fast OLTP

Tradeoffs:

- Durability requires snapshotting/logging; memory cost and failure modes matter
    

### 11) Vector databases (AI-era)

**Model:** vectors (embeddings) + metadata  

**Strengths:** similarity search (nearest neighbors), hybrid search (vector + filters/text)  

**Best for:** semantic search, RAG systems, recommendation, deduplication, clustering

Tradeoffs:

- Typically not your transactional system of record; commonly paired with relational/document stores
    

#### “System of record”

The authoritative source of truth for some domain (e.g., payments ledger, orders). Usually demands strong correctness guarantees and auditability.
