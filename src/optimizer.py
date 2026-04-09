"""
optimizer.py
------------
Applies composite and covering indexes to the load_simulator database.
Run this AFTER benchmarking slow queries (query_bench.py --mode before)
and BEFORE re-benchmarking (query_bench.py --mode after).

Usage:
    python src/optimizer.py
"""

import os
import time
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

INDEXES = [
    {
        "name":  "idx_orders_user_date",
        "table": "orders",
        "ddl":   "CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC)",
        "reason":"Covers Q1: user_id equality + created_at ORDER BY - eliminates filesort",
    },
    {
        "name":  "idx_orders_product",
        "table": "orders",
        "ddl":   "CREATE INDEX idx_orders_product ON orders (product_id)",
        "reason":"Covers Q2 JOIN on product_id after N+1 rewrite to LEFT JOIN + GROUP BY",
    },
    {
        "name":  "idx_orders_date",
        "table": "orders",
        "ddl":   "CREATE INDEX idx_orders_date ON orders (created_at)",
        "reason":"Covers Q3 date range scan; reduces full-table scan to range scan",
    },
    {
        "name":  "idx_orders_status_date",
        "table": "orders",
        "ddl":   "CREATE INDEX idx_orders_status_date ON orders (status, created_at DESC)",
        "reason":"Covers Q4: status equality + created_at ORDER BY - covering index",
    },
    {
        "name":  "idx_products_category",
        "table": "products",
        "ddl":   "CREATE INDEX idx_products_category ON products (category)",
        "reason":"Covers Q2 WHERE category = '...' filter on products table",
    },
]


def index_exists(cursor, index_name, table_name):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.statistics "
        "WHERE table_schema = DATABASE() AND table_name = %s AND index_name = %s",
        (table_name, index_name),
    )
    return cursor.fetchone()[0] > 0


def apply_indexes(conn):
    cursor  = conn.cursor()
    results = []
    print("Applying indexes...\n")
    for idx in INDEXES:
        if index_exists(cursor, idx["name"], idx["table"]):
            status = "SKIPPED (already exists)"
        else:
            t0 = time.time()
            cursor.execute(idx["ddl"])
            conn.commit()
            elapsed = time.time() - t0
            status = f"CREATED in {elapsed:.2f}s"
        results.append([idx["name"], idx["table"], status, idx["reason"]])
        print(f"  {idx['name']}: {status}")
    cursor.close()
    return results


def show_index_summary(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT table_name, index_name, GROUP_CONCAT(column_name ORDER BY seq_in_index) AS columns "
        "FROM information_schema.statistics "
        "WHERE table_schema = DATABASE() AND index_name != 'PRIMARY' "
        "GROUP BY table_name, index_name ORDER BY table_name, index_name"
    )
    rows = cursor.fetchall()
    cursor.close()
    print("\nAll non-primary indexes on the schema:")
    print(tabulate(rows, headers=["Table","Index Name","Columns"], tablefmt="rounded_outline"))


if __name__ == "__main__":
    print("MySQL Load Simulator - Index Optimizer")
    conn    = mysql.connector.connect(**DB_CONFIG)
    results = apply_indexes(conn)
    show_index_summary(conn)
    conn.close()
    print("\nOptimization complete. Now run: python src/query_bench.py --mode after")
