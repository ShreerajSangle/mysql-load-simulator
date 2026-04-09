"""
query_bench.py
--------------
Benchmarks slow vs optimized queries.
Runs each query 10 times, records min/avg/max latency, writes results to benchmark_log.

Usage:
    python src/query_bench.py --mode before
    python src/query_bench.py --mode after
    python src/query_bench.py --mode before --explain
"""

import os
import sys
import time
import argparse
import mysql.connector
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "load_simulator"),
    "user":     os.getenv("MYSQL_USER", "labuser"),
    "password": os.getenv("MYSQL_PASSWORD", "labpassword"),
}

RUNS = 10

QUERIES = {
    "Q1_user_orders": """
        SELECT o.order_id, o.total_price, o.status, o.created_at
        FROM orders o
        WHERE o.user_id = 1234
        ORDER BY o.created_at DESC
        LIMIT 20
    """,
    "Q2_product_order_count": """
        SELECT p.name,
               (SELECT COUNT(*) FROM orders o WHERE o.product_id = p.product_id) AS order_count
        FROM products p
        WHERE p.category = 'Electronics'
        LIMIT 100
    """,
    "Q3_revenue_by_date": """
        SELECT DATE(created_at) AS order_date,
               COUNT(*) AS total_orders,
               SUM(total_price) AS revenue
        FROM orders
        WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
        GROUP BY DATE(created_at)
        ORDER BY order_date
    """,
    "Q4_pending_orders": """
        SELECT user_id, order_id, total_price
        FROM orders
        WHERE status = 'pending'
        ORDER BY created_at DESC
        LIMIT 100
    """,
}


def benchmark_query(cursor, name, sql, runs=RUNS):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        cursor.execute(sql)
        cursor.fetchall()
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "query_name": name,
        "avg_ms":     round(sum(times) / len(times), 3),
        "min_ms":     round(min(times), 3),
        "max_ms":     round(max(times), 3),
    }


def log_results(conn, phase, results):
    cursor = conn.cursor()
    for r in results:
        cursor.execute(
            "INSERT INTO benchmark_log (phase, query_name, avg_ms, min_ms, max_ms) VALUES (%s,%s,%s,%s,%s)",
            (phase, r["query_name"], r["avg_ms"], r["min_ms"], r["max_ms"]),
        )
    conn.commit()
    cursor.close()


def explain_query(cursor, name, sql):
    print(f"\n-- EXPLAIN: {name} --")
    cursor.execute(f"EXPLAIN {sql.strip()}")
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    print(tabulate(rows, headers=cols, tablefmt="simple"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MySQL Query Benchmarker")
    parser.add_argument("--mode", choices=["before","after"], default="before")
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()

    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print(f"Query Benchmarker - Phase: {args.mode}")
    print(f"Running each query {RUNS}x to average latency...")

    bench_results = []
    for name, sql in QUERIES.items():
        print(f"  Benchmarking {name}...", end="", flush=True)
        result = benchmark_query(cursor, name, sql)
        bench_results.append(result)
        print(f" avg={result['avg_ms']:.1f}ms")
        if args.explain:
            explain_query(cursor, name, sql)

    cursor.close()
    log_results(conn, args.mode, bench_results)
    conn.close()

    headers = ["Query","Avg (ms)","Min (ms)","Max (ms)"]
    rows    = [[r["query_name"],r["avg_ms"],r["min_ms"],r["max_ms"]] for r in bench_results]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline", floatfmt=".3f"))
    print(f"Results logged to benchmark_log (phase='{args.mode}')")
