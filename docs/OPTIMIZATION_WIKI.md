# MySQL Optimization Engineering Wiki

> Personal engineering log — MySQL Load Simulator self-learning project  
> Author: Shreeraj Sangle | Started: Week 1

---

## Week 1 — Environment Setup

**Goal:** Get a reproducible MySQL 8.0 environment running locally.

- Installed Docker Desktop and wrote `docker-compose.yml` with MySQL 8.0 + phpMyAdmin
- Created `.env.example` for credential management — learned why hardcoding DB creds is a security issue
- Applied `sql/schema.sql` manually first time using `mysql -h 127.0.0.1 -u root -p`
- **Key insight:** Using `ENGINE=InnoDB` is mandatory for foreign keys and transactions

---

## Week 2 — Synthetic Data Generation

**Goal:** Generate 500,000 realistic rows without crashing MySQL.

- Used Python `Faker` library to generate users, products, orders, events
- First attempt: single-row INSERTs — took 45 minutes. Switched to batched INSERTs (5,000 rows/commit)
- New time: ~4 minutes for 500K rows — **10x improvement from batching alone**
- Learned about `AUTO_INCREMENT` gaps when rollbacks occur
- **Key insight:** Always commit in batches. Each `conn.commit()` flushes to disk — too many = slow, too few = memory pressure

---

## Week 3 — Baseline Benchmarking

**Goal:** Measure real query latency before any optimization.

**Baseline results (before indexes):**

| Query | Avg (ms) | Type |
|-------|----------|------|
| Q1 user orders | ~850ms | Full table scan |
| Q2 product N+1 | ~3200ms | Correlated subquery |
| Q3 revenue date | ~1100ms | Full scan + filesort |
| Q4 pending status | ~920ms | Full scan |

- Used `EXPLAIN` to confirm `type: ALL` on every query
- Learned what `rows` column in EXPLAIN means — MySQL's estimate of rows it will examine
- **Key insight:** `type: ALL` in EXPLAIN = full table scan = problem

---

## Week 4 — Index Strategy

**Goal:** Design and apply the right indexes for each query pattern.

**Indexes applied via `src/optimizer.py`:**

1. `idx_orders_user_date (user_id, created_at DESC)` — composite for Q1
2. `idx_orders_product (product_id)` — for JOIN in Q2 rewrite
3. `idx_orders_date (created_at)` — range scan for Q3
4. `idx_orders_status_date (status, created_at DESC)` — covering index for Q4
5. `idx_products_category (category)` — for Q2 filter

**Lessons learned:**
- Left-prefix rule: `(user_id, created_at)` helps `WHERE user_id=X ORDER BY created_at` but NOT `WHERE created_at=Y` alone
- Covering index = all columns needed by query are IN the index — no table lookup needed
- Adding too many indexes slows down INSERTs/UPDATEs — balance is key

---

## Week 5 — Query Rewriting

**Goal:** Fix the N+1 correlated subquery in Q2.

**Before (N+1 pattern):**
```sql
SELECT p.name,
  (SELECT COUNT(*) FROM orders o WHERE o.product_id = p.product_id) AS cnt
FROM products p WHERE p.category = 'Electronics';
```

**After (single JOIN + GROUP BY):**
```sql
SELECT p.name, COUNT(o.order_id) AS cnt
FROM products p
LEFT JOIN orders o ON o.product_id = p.product_id
WHERE p.category = 'Electronics'
GROUP BY p.product_id, p.name;
```

- The correlated subquery executed once **per product row** — 500+ subquery calls
- The JOIN version executes as a single pass — one query, one result set
- **Key insight:** If you see a subquery in the SELECT clause referencing the outer table, it's almost always an N+1 pattern

---

## Week 6 — Final Results

**After indexes + query rewrites:**

| Query | Before (ms) | After (ms) | Improvement |
|-------|-------------|------------|-------------|
| Q1 user orders | ~850ms | ~12ms | **98.6% faster** |
| Q2 N+1 rewrite | ~3200ms | ~45ms | **98.6% faster** |
| Q3 revenue date | ~1100ms | ~180ms | **83.6% faster** |
| Q4 pending status | ~920ms | ~15ms | **98.4% faster** |
| **Average** | **~1518ms** | **~63ms** | **~84% faster** |

**Final takeaways:**
- Indexes are the single highest-leverage optimization in MySQL
- EXPLAIN before you index — don't guess
- N+1 queries are invisible until you measure at scale
- Batched writes + connection pooling matter for write-heavy workloads
