# Media Files in Databases

### What they are and how they are typically handled

In [Materials 03](./Materials/03-Relational-Database.md) we introduced the relational model and common data types (integers, text, dates).  
In [Materials 05](./Materials/05-SQL-fundamentals.md)–[07](./Materials/07-SQL-fundamentals-3.md) we worked with structured data in tables.

This chapter introduces **media files** in the context of databases:

- **What media files are** — definition, types, and characteristics
- **Why they are different** — challenges compared to structured data
- **Storage approaches** — storing in the database vs. the file system
- **Schema design patterns** — how to model and reference media in tables
- **Best practices and trade-offs** — size limits, backups, performance, and security

---

# 1) What Are Media Files?

**Media files** are binary or semi-structured files that represent audio, visual, or document content. They appear everywhere in modern applications: profile pictures, product photos, podcast episodes, video tutorials, downloadable PDFs, and scanned documents. Unlike the structured data (numbers, text, dates) we store in typical database columns, media files have distinct characteristics that affect how we store, retrieve, and manage them.

---

## Defining characteristics of media files

Media files differ from plain text and numeric data in several important ways:

### Size

- Media files range from **kilobytes** (small icons, thumbnails) to **gigabytes** (raw video, high-resolution scans).
- A single photo from a smartphone can be 3–10 MB; a feature-length movie can be several GB.
- Database columns are usually designed for values measured in bytes to a few kilobytes. Large media blobs strain storage, backup, and query performance.

### Binary storage

- Media content is stored as **raw bytes** — binary data that is not meant to be read as human-readable text.
- Some formats (e.g., SVG, XML-based formats) are technically text-based but still treated as opaque assets by most applications.
- The database stores the bytes; it does not parse, validate, or interpret the content. That is the job of specialized software (image decoders, media players, document viewers).

### Format-dependent interpretation

- Each format has its own structure: headers, compression, streams, metadata blocks.
- **JPEG** uses DCT compression; **MP3** uses perceptual audio coding; **MP4** is a container that can hold H.264 video and AAC audio.
- To display or process a file, you need software that understands that format. The database does not provide this — it only stores and retrieves the bytes.

### Metadata-rich

- Most media formats embed **metadata** alongside the raw content:
  - **Images:** dimensions (width × height), color depth, orientation, camera make/model, GPS coordinates
  - **Audio:** duration, bitrate, sample rate, artist, album
  - **Video:** duration, resolution, codec, frame rate
- This metadata is often extracted and stored separately in the database for querying and filtering (e.g., "find all images wider than 1920px" or "list videos longer than 10 minutes").

---

## Common types of media files

Different media categories have different storage needs, typical sizes, and use cases in applications.

| Category    | Examples                     | Typical extensions       | Typical size range   |
| ----------- | ---------------------------- | ------------------------ | -------------------- |
| **Images**  | Photos, icons, thumbnails    | `.jpg`, `.png`, `.gif`, `.webp`, `.svg` | 10 KB – 50 MB        |
| **Audio**   | Music, podcasts, recordings  | `.mp3`, `.wav`, `.ogg`, `.m4a`          | 100 KB – 100 MB      |
| **Video**   | Movies, clips, live streams  | `.mp4`, `.webm`, `.avi`, `.mkv`         | 1 MB – 10+ GB        |
| **Documents** | PDFs, Office files         | `.pdf`, `.docx`, `.xlsx`, `.pptx`       | 10 KB – 100 MB       |
| **Archives**  | Zip, tarballs              | `.zip`, `.tar.gz`, `.7z`                | Variable             |

### Images

- **Raster images** (JPEG, PNG, GIF, WebP): pixel grids; size grows with resolution and color depth. Often compressed (lossy for photos, lossless for graphics).
- **Vector images** (SVG): stored as text/XML; scalable without quality loss; typically smaller for logos and icons.
- Common use: avatars, product galleries, thumbnails, infographics, charts.

### Audio

- **Compressed** (MP3, AAC, OGG): smaller files, suitable for streaming and storage. Quality depends on bitrate.
- **Uncompressed** (WAV, FLAC): larger, used when quality or editing is critical.
- Common use: podcast episodes, music tracks, voice memos, sound effects, audiobooks.

### Video

- Video files are usually the **largest** media type. A few minutes of HD footage can exceed 100 MB.
- Many video formats are **containers** (e.g., MP4, MKV, WebM) that bundle:
  - One or more video streams (e.g., H.264, VP9)
  - One or more audio streams (e.g., AAC, Opus)
  - Optional subtitles, chapters, and metadata
- Common use: course lectures, marketing clips, user-generated content, surveillance footage.

### Documents

- PDFs and Office files (.docx, .xlsx, .pptx) are **compound formats**: internally they may contain text, images, fonts, and embedded objects.
- Size varies widely: a simple text PDF might be 50 KB; a scanned book could be hundreds of MB.
- Common use: contracts, reports, manuals, spreadsheets, presentations.

### Archives

- Zip, tar.gz, 7z: bundles of other files, often compressed. Size depends entirely on contents.
- Sometimes used to store multiple related files (e.g., a "package" of documents) or to reduce transfer size.

---

## Container formats vs. single-purpose formats

- **Container formats** (MP4, MKV, WebM, OGG) act as wrappers: they hold multiple streams (video + audio + subtitles) and metadata in a single file. The same container can carry different codecs inside.
- **Single-purpose formats** (JPEG, PNG, MP3, WAV) store one type of content. Simpler, but less flexible.

---

## Media vs. structured data

In a relational database, most columns hold **structured data**:

- Integers, decimals, dates, short text strings
- Small, fixed or bounded size (typically bytes to a few KB)
- Directly comparable, sortable, and indexable
- Fits naturally in rows and columns; the database can efficiently filter, join, and aggregate

Media files are **unstructured** (or semi-structured) from the database’s perspective:

- The database does not “understand” the content — it cannot parse a JPEG or decode an MP3
- Size can vary enormously, from a few KB to many GB
- You rarely query *inside* the bytes (e.g., “find all MP3s where the chorus mentions X”) — that would require full-text search over decoded content or specialized systems
- You *do* query **metadata** (e.g., “find all images uploaded by user X” or “find videos longer than 10 minutes”)

So the database’s role with media is usually to **store references and metadata**, not to interpret or search the raw content. The actual bytes live either inside the database as a BLOB or, more commonly, in external storage (file system or object storage) that the database points to.

---

# 2) Why Media Files Are Different

Relational databases excel at storing and querying structured data: rows of integers, text, and dates that fit neatly in tables and benefit from indexes, joins, and transactions. Media files, however, have different properties—size, access patterns, and lifecycle—that clash with how databases are designed and operated. Understanding these tensions helps explain why storing media *inside* the database is often a poor fit, and why many systems keep media on the file system or in object storage instead.

---

## Size and storage

- **Scale mismatch:** A single high-resolution video can exceed 1 GB. A typical database row is measured in bytes to a few kilobytes. Storing hundreds or thousands of media files as BLOBs quickly makes the database orders of magnitude larger than its core transactional data.
- **Optimization targets:** Databases are tuned for small to medium row sizes. Large BLOBs can cause page bloat, inefficient buffer cache usage, and slower sequential scans when the optimizer touches BLOB columns.
- **Backup and replication:** Every full backup includes the media bytes. Replication streams must transfer them. A 100 GB database of metadata becomes a 1 TB database when you add 900 GB of embedded media—backup windows and restore times grow accordingly.
- **Database limits:** Many systems impose per-value limits (e.g., PostgreSQL `BYTEA` up to 1 GB, MySQL `BLOB` up to 64 KB by default unless configured for `MEDIUMBLOB` or `LONGBLOB`). Very large files may not fit at all, or require special tuning.
- **Write-ahead logging (WAL):** Some databases log BLOB changes for durability. Large BLOBs can inflate WAL volume and complicate point-in-time recovery.

---

## Access patterns

- **Structured data:** You fetch a row, read a few columns, and use the values in your application. The operation is small, fast, and transactional.
- **Media:** Users often need to **stream** content—start playing a video or audio before the entire file is downloaded—or **seek** within a file (jump to a specific timestamp). Web servers and CDNs support **HTTP range requests** (e.g., "give me bytes 1,000,000–2,000,000"), which allow partial downloads and efficient seeking. Databases are built for full-value reads and transactional semantics, not for high-throughput sequential streaming of large byte ranges to many concurrent clients.
- **Concurrency:** A popular video might be requested thousands of times per minute. Each request would tie up a database connection and read the same multi‑hundred‑MB blob repeatedly. Database connection pools and I/O bandwidth are not designed for this workload; dedicated media servers and CDNs are.
- **Latency:** Applications typically want low latency for metadata ("show me the list of videos") but can tolerate higher latency for the media itself ("start buffering the video"). Splitting metadata (in the DB) from media (in storage) lets you optimize each path independently.

---

## Caching and content delivery

- **Geographic distribution:** Images and videos benefit from **CDNs** (Content Delivery Networks)—networks of edge servers placed close to users worldwide. A user in Tokyo receives a video from a Tokyo edge server instead of from a single central database, reducing latency and cross-continental bandwidth.
- **Caching behavior:** Media files are often **immutable** (the same URL always returns the same bytes). That makes them ideal for caching: once cached at the edge, subsequent requests never hit the origin. Database results can be cached too, but cache invalidation is trickier when data changes frequently.
- **Cost and load:** Serving media from a CDN is faster for users and cheaper for you—CDN egress is typically less expensive than database I/O, and you avoid loading the database with high-volume media traffic. Database servers are better reserved for transactional and query workloads.
- **No database in the hot path:** When media lives in object storage (e.g., S3, Azure Blob) or a file system, the application fetches the URL from the database once, then the browser or app requests the media directly from storage or the CDN. The database is not in the critical path for every media request.

---

## Backup and recovery

- **Backup size and duration:** Large media blobs inflate backup size and duration. A nightly full backup that takes 10 minutes without media might take hours with hundreds of GB of embedded files. Incremental backups can help, but BLOB-heavy tables still dominate backup size.
- **Restore granularity:** Restoring a full backup just to recover a few rows of metadata—or a single corrupted file—is inefficient. With media in external storage, you can restore the database (metadata) and storage (files) independently, and only restore what failed.
- **Retention and archiving:** Media files often have different retention and archiving needs than transactional data. Legal or policy may require keeping documents for 7 years but purging access logs after 90 days. Mixing media and transactional data in one backup complicates retention policies and compliance.
- **Recovery objectives:** **RTO** (Recovery Time Objective) and **RPO** (Recovery Point Objective) may differ for metadata vs. media. You might need metadata restored within minutes, but media can be restored over hours from separate archives. Co-locating them forces a single recovery strategy for both.

---

# 3) Storage Approaches

The core design question is: **where do the actual bytes live?** You can store media **inside** the database as binary data, or **outside** the database (on disk or in object storage) and keep only a reference and metadata in the DB. The choice affects consistency, performance, scalability, and operations. There is no single right answer—it depends on file size, volume, access patterns, and operational constraints.

---

## Approach 1: Store media inside the database (BLOB)

Store the raw bytes in a column with a binary type. The file and its metadata reside in the same table; the database is the single source of truth for both.

### Database types for binary data

| Database   | Type            | Typical limit                          |
| ---------- | --------------- | -------------------------------------- |
| PostgreSQL | `BYTEA`         | ~1 GB per value                        |
| PostgreSQL | `bytea` with TOAST | Large values stored out-of-line automatically |
| MySQL      | `BLOB`          | 64 KB (default); `MEDIUMBLOB` 16 MB; `LONGBLOB` 4 GB |
| SQL Server | `VARBINARY(MAX)`| 2 GB                                    |

PostgreSQL uses **TOAST** (The Oversized-Attribute Storage Technique) for values larger than ~2 KB: the main table stores a reference, and the actual bytes live in a separate TOAST table. This keeps the main table compact but still stores everything in the database.

### Schema sketch

```
┌────────────────────────────────────────────────────────────┐
│  media_files                                               │
├──────────┬──────────┬──────────┬───────────┬───────────────┤
│ id       │ name     │ mime_type│ size_bytes│ file_content  │  ← binary data
│ 1        │ photo.jpg│ image/…  │ 245000    │ <0xFFD8FFE0…> │
└──────────┴──────────┴──────────┴───────────┴───────────────┘
```

### Pros

- **Single source of truth** — file and metadata in one place; no external system to coordinate
- **Transactional consistency** — insert, update, or delete file and metadata in one transaction; no risk of row without file or file without row
- **Simpler backup** — one backup contains everything (though it can be huge)
- **No orphaned files** — deleting a row removes the file automatically; no cleanup jobs needed
- **Access control** — database roles and privileges apply to the file; no separate storage permissions to manage

### Cons

- **Large database size** — backups, replication, and storage costs grow quickly with media volume
- **Performance** — reading large blobs loads data through the database; not ideal for streaming or high concurrency
- **Connection overhead** — fetching a 100 MB file ties up a database connection for the duration of the transfer
- **Size limits** — per-database limits apply; very large files may not fit or require special configuration
- **Poor fit for CDNs** — media is trapped in the DB; you cannot point a CDN origin at a database table
- **WAL and replication** — large inserts/updates increase WAL volume and replication lag

### When to use

- **Small files** — e.g., thumbnails, icons, or tiny documents under ~100 KB
- **Strong consistency requirement** — e.g., regulatory or audit needs (e.g., “file and metadata must always match”)
- **Low volume** — dozens or hundreds of files, not millions
- **Simple deployment** — no desire to operate object storage or a separate media service
- **No streaming or CDN need** — files are small enough that full download is acceptable

---

## Approach 2: Store media on the file system (or object storage), reference in DB

Store the file **outside** the database: on a local or network-mounted disk, or in **object storage** (Amazon S3, Azure Blob Storage, Google Cloud Storage, MinIO, etc.). In the database, store only:

- A **path** or **URL** to the file (e.g., `/media/products/123/abc-def.jpg` or `s3://bucket/media/123/abc-def.jpg`)
- **Metadata** (name, size, MIME type, dimensions, duration, upload time, checksum, etc.)

The database holds the *index*; the storage holds the *content*.

### File system vs. object storage

| Aspect           | File system (disk, NFS)      | Object storage (S3, Azure Blob)          |
| ---------------- | ---------------------------- | ---------------------------------------- |
| **Access model** | Path-based (e.g., `/media/…`)| Key-based (e.g., `bucket/key`)           |
| **Scaling**      | Limited by disk/server       | Designed for massive scale               |
| **Durability**   | Depends on RAID/backup       | Built-in replication, versioning         |
| **HTTP access**  | Requires web server          | Native HTTP(S) APIs, signed URLs         |
| **Cost**         | Disk cost                    | Per-GB storage + egress                  |
| **Typical use**  | Single server, simple setups | Cloud apps, multi-region, CDN origins    |

Object storage is built for unstructured data at scale: you put objects in, get them out by key, and the provider handles durability and availability. Most CDNs can use object storage as the origin.

### Schema sketch

```
┌────────────────────────────────────────────────────────────┐
│  media_files (database)                                    │
├──────────┬──────────┬──────────┬───────────┬───────────────┤
│ id       │ name     │ mime_type│ size_bytes│ file_path     │  ← reference only
│ 1        │ photo.jpg│ image/…  │ 245000    │ /media/1/…    │
└──────────┴──────────┴──────────┴───────────┴───────────────┘

┌────────────────────────────────────────────────────────────┐
│  File system / Object storage                              │
├────────────────────────────────────────────────────────────┤
│  /media/1/abc123-photo.jpg  (actual bytes on disk/S3)      │
└────────────────────────────────────────────────────────────┘
```

### Pros

- **Database stays small** — only metadata and references; no bloat from binary content
- **Faster backups** — DB backup is quick; media can be backed up or replicated separately
- **Streaming-friendly** — web server or CDN serves files directly; HTTP range requests, byte-range serving
- **CDN integration** — point CDN at storage; cache at edge; reduce origin load
- **Scaling** — object storage scales independently; add capacity without touching the database
- **No BLOB size limits** — file size is limited by storage, not by database constraints
- **Cheaper at scale** — object storage and CDN egress often cost less than database I/O for large media

### Cons

- **Two places to manage** — file and DB row can get out of sync: orphaned files (file exists, no row), broken references (row points to missing file), or duplicated uploads
- **No built-in transactions** — uploading a file and inserting a row are separate steps; need application-level logic (e.g., upload first, then insert; or insert with placeholder, then update) and cleanup jobs for failures
- **Path/URL design** — must decide naming (UUIDs, IDs), versioning, and access patterns (public vs. signed URLs)
- **Access control** — storage permissions are separate from database roles; often implemented via signed URLs with expiration

### Operational considerations

- **Signed URLs:** Object storage often uses **signed URLs** (time-limited, tokenized URLs) so you can grant temporary access without making objects public. The application generates a signed URL from the DB reference and returns it to the client.
- **Orphan cleanup:** Periodic jobs can find files in storage with no matching DB row (or vice versa) and clean them up.
- **Idempotent uploads:** Use deterministic keys (e.g., content hash) so re-uploading the same file does not create duplicates.

### When to use

- **Medium to large files** — images, audio, video, documents
- **High volume or high traffic** — thousands of files or many concurrent viewers
- **Streaming, CDN, or efficient delivery** — need range requests, edge caching, or low latency
- **Most production applications** — the de facto choice for user-generated content, product catalogs, and media-heavy apps

---

## Hybrid approach

Combine both strategies: store **metadata and a reference** in the database, and the **full file** in object storage. Optionally store **small thumbnails or previews** as BLOBs in the DB for quick display in lists or grids.

### Example

- **Full image** (2 MB) → object storage, referenced by URL in `media_files.file_path`
- **Thumbnail** (15 KB) → BLOB in `media_files.thumbnail_content` for fast rendering in list views

Benefits: you get transactional consistency for the small preview (no extra HTTP request for list views) while keeping the large file in storage for full-size display and CDN delivery. The trade-off is added schema complexity and the need to generate and store thumbnails on upload.

---

# 4) Schema Design Patterns

When using the **reference approach** (file outside DB), the database stores metadata and a pointer. Here are common patterns.

---

## Basic media table

```sql
CREATE TABLE media_files (
    id           SERIAL PRIMARY KEY,
    filename     VARCHAR(255) NOT NULL,
    mime_type    VARCHAR(100) NOT NULL,
    size_bytes   BIGINT NOT NULL,
    file_path    VARCHAR(500) NOT NULL,   -- or storage_url for S3, etc.
    uploaded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by  INTEGER REFERENCES users(id)
);
```

- `file_path` or `storage_url`: path on disk or URL in object storage
- `mime_type`: e.g., `image/jpeg`, `video/mp4` — used for HTTP `Content-Type`
- `size_bytes`: useful for quotas, UI, and validation

---

## Media linked to entities

Media is often associated with other entities (user avatar, product image, document attachment).

```sql
-- Product images: one product, many images
CREATE TABLE product_images (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    filename    VARCHAR(255) NOT NULL,
    mime_type   VARCHAR(100) NOT NULL,
    file_path   VARCHAR(500) NOT NULL,
    sort_order  INTEGER DEFAULT 0,    -- for ordering (e.g. primary image first)
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User avatar: one-to-one
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL,
    avatar_path   VARCHAR(500),       -- nullable; user may have no avatar
    -- ...
);
```

---

## Separate metadata for different media types

For richer metadata (e.g., image dimensions, video duration), you can extend the schema:

```sql
CREATE TABLE images (
    id          SERIAL PRIMARY KEY,
    file_path   VARCHAR(500) NOT NULL,
    width_px    INTEGER,
    height_px   INTEGER,
    -- ...
);

CREATE TABLE videos (
    id           SERIAL PRIMARY KEY,
    file_path    VARCHAR(500) NOT NULL,
    duration_sec INTEGER,
    width_px     INTEGER,
    height_px    INTEGER,
    codec        VARCHAR(50),
    -- ...
);
```

Alternatively, use a single `media_files` table with nullable columns for type-specific fields, or a generic `metadata` JSONB column.

---

# 5) Considerations and Best Practices

---

## File naming and paths

- **Avoid collisions:** Use UUIDs or composite keys (e.g., `{id}-{uuid}.{ext}`) so two uploads never overwrite each other.
- **Organize by context:** e.g., `/media/products/123/`, `/media/users/456/avatars/`
- **Include extension:** Keeps MIME logic simple and helps clients and CDNs.

---

## Consistency when using external storage

- **Upload flow:**  
  1. Save file to storage.  
  2. Insert row with path/URL.  
  If step 2 fails, you have an orphaned file — run periodic cleanup jobs.
- **Delete flow:**  
  1. Delete row.  
  2. Delete file.  
  If step 2 fails, you have a stranded file — same cleanup approach.
- **Transactions:** Some object stores support transactional APIs; otherwise, design for eventual consistency and cleanup.

---

## Size limits and validation

- Validate file size and type **before** storing (in the application).
- Set limits per file type (e.g., avatars max 2 MB, documents max 50 MB).
- Use `CHECK` constraints for metadata where possible, e.g. `size_bytes > 0 AND size_bytes <= 104857600`.

---

## Security

- **Do not trust user-provided filenames** — sanitize or generate safe names to avoid path traversal (e.g., `../../../etc/passwd`).
- **Validate MIME types** — don’t rely only on extension; check magic bytes or a trusted library.
- **Control access** — serve files through the application or signed URLs so you can enforce authorization.
- **Scan for malware** — for user uploads, consider virus scanning before storing.

---

## Backups

- **Database:** Back up metadata tables normally; keep them small and fast to restore.
- **Media files:** Back up storage separately (object storage often has built-in versioning and cross-region replication).
- **Sync:** Document how to recover if DB and storage are restored from different points in time.

---

# 6) Summary

| Aspect              | BLOB in database                    | File system / object storage + reference      |
| ------------------- | ----------------------------------- | --------------------------------------------- |
| **Use case**        | Small files, strong consistency     | Medium/large files, high volume, streaming    |
| **DB size**         | Grows with media                    | Stays small                                   |
| **Backup**          | Single backup, but large            | DB and storage backed up separately           |
| **Streaming/CDN**   | Awkward                             | Natural fit                                   |
| **Consistency**     | Atomic                              | Application-managed, may need cleanup         |
| **Scalability**     | Limited by DB                       | Storage scales independently                  |

**Recommendation:** For most applications, store media files in object storage (or a file system) and keep only metadata and a path/URL in the database. Use BLOBs only when files are small, few, and transactional consistency is critical.

---

## Related materials

- [Materials 03](./Materials/03-Relational-Database.md) — Relational model and data types
- [Materials 08](./Materials/08-Normalization-and-Schema-Quality.md) — Schema design and avoiding redundancy
- [Materials 12](./Materials/12-Databases-in-Programming.md) — How applications interact with databases
