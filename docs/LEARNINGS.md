# Self-Learning Quick Reference

Key MySQL concepts studied independently during this project.

---

## EXPLAIN Output — What to Look For

| Column | Good | Bad |
|--------|------|-----|
| `type` | `ref`, `range`, `eq_ref` | `ALL` (full table scan) |
| `key` | Any index name | `NULL` (no index used) |
| `rows` | Low number | Close to total table rows |
| `Extra` | `Using index` | `Using filesort`, `Using temporary` |

---

## Index Types Studied

1. **B-Tree (default)** — best for equality (`=`) and range (`BETWEEN`, `>`, `<`) queries
2. **Composite Index** — multiple columns; left-prefix rule applies
3. **Covering Index** — all columns needed by the query live inside the index (no table lookup)
4. **Full-Text Index** — for `MATCH ... AGAINST` text search

---

## Query Optimization Checklist

- [ ] Run `EXPLAIN` on every slow query first
- [ ] Look for `type: ALL` — that's a full table scan
- [ ] Add indexes on columns in `WHERE`, `ORDER BY`, `JOIN ON`
- [ ] Replace correlated subqueries in SELECT with `LEFT JOIN + GROUP BY`
- [ ] Avoid `SELECT *` — fetch only needed columns
- [ ] Use `LIMIT` on large result sets
- [ ] Use half-open ranges (`>=` and `<`) instead of `BETWEEN` for dates
- [ ] Verify index is actually used with `EXPLAIN` after creation

---

## Key Commands Used

```sql
-- See query execution plan
EXPLAIN SELECT ...;

-- Check all indexes on a table
SHOW INDEX FROM orders;

-- Check table size
SELECT table_name, ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'load_simulator';
```
