-- ============================================================
-- optimized_queries.sql  --  FAST queries (after indexing)
-- Run with: python src/query_bench.py --mode after
-- ============================================================
USE load_simulator;

-- Q1: Uses composite index idx_orders_user_date (user_id, created_at)
SELECT o.order_id, o.total_price, o.status, o.created_at
FROM orders o
WHERE o.user_id = 1234
ORDER BY o.created_at DESC
LIMIT 20;

-- Q2: JOIN + GROUP BY replaces correlated subquery (N+1 eliminated)
SELECT p.name, COUNT(o.order_id) AS order_count
FROM products p
LEFT JOIN orders o ON o.product_id = p.product_id
WHERE p.category = 'Electronics'
GROUP BY p.product_id, p.name;

-- Q3: Half-open range avoids BETWEEN edge issues; uses idx_orders_date
SELECT DATE(created_at) AS order_date,
       COUNT(*)          AS total_orders,
       SUM(total_price)  AS revenue
FROM orders
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
GROUP BY DATE(created_at)
ORDER BY order_date;

-- Q4: Uses composite covering index idx_orders_status_date
SELECT user_id, order_id, total_price
FROM orders
WHERE status = 'pending'
ORDER BY created_at DESC
LIMIT 100;
