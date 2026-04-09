-- ============================================================
-- seed_queries.sql  --  SLOW / UNOPTIMIZED queries (before)
-- Run with: python src/query_bench.py --mode before
-- ============================================================
USE load_simulator;

-- Q1: Fetch recent orders for a user (no index on user_id)
SELECT o.order_id, o.total_price, o.status, o.created_at
FROM orders o
WHERE o.user_id = 1234
ORDER BY o.created_at DESC
LIMIT 20;

-- Q2: N+1 anti-pattern - correlated subquery per product row
SELECT p.name,
       (SELECT COUNT(*) FROM orders o WHERE o.product_id = p.product_id) AS order_count
FROM products p
WHERE p.category = 'Electronics';

-- Q3: Date range revenue report (no index on created_at)
SELECT DATE(created_at) AS order_date,
       COUNT(*)          AS total_orders,
       SUM(total_price)  AS revenue
FROM orders
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY DATE(created_at)
ORDER BY order_date;

-- Q4: Status filter (no index on status)
SELECT user_id, order_id, total_price
FROM orders
WHERE status = 'pending'
ORDER BY created_at DESC
LIMIT 100;
