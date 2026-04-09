"""
data_gen.py
-----------
Generates 500,000 synthetic rows replicating production-level e-commerce traffic.
Uses Faker library for realistic data and batched INSERTs for performance.

Usage:
    python src/data_gen.py
"""

import os
import time
import random
from datetime import datetime
from faker import Faker
import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
fake = Faker()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "load_simulator"),
    "user":     os.getenv("MYSQL_USER", "labuser"),
    "password": os.getenv("MYSQL_PASSWORD", "labpassword"),
}

BATCH_SIZE   = int(os.getenv("BATCH_SIZE", 5000))
NUM_USERS    = 50_000
NUM_PRODUCTS = 5_000
NUM_ORDERS   = 500_000
NUM_EVENTS   = 200_000

CATEGORIES  = ["Electronics","Clothing","Home & Garden","Sports","Books","Toys","Food","Beauty"]
STATUSES    = ["pending","processing","shipped","delivered","cancelled"]
EVENT_TYPES = ["page_view","add_to_cart","checkout_start","purchase","search"]


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def seed_users(conn, n=NUM_USERS):
    print(f"\n[1/4] Seeding {n:,} users...")
    cursor = conn.cursor()
    batch = []
    for i in tqdm(range(n), unit="rows"):
        batch.append((
            fake.user_name()[:100],
            fake.unique.email()[:255],
            fake.country()[:80],
            fake.date_time_between(start_date="-3y", end_date="now"),
            random.choice([1, 1, 1, 0]),
        ))
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(
                "INSERT INTO users (username, email, country, created_at, is_active) VALUES (%s,%s,%s,%s,%s)",
                batch,
            )
            conn.commit()
            batch.clear()
    if batch:
        cursor.executemany(
            "INSERT INTO users (username, email, country, created_at, is_active) VALUES (%s,%s,%s,%s,%s)",
            batch,
        )
        conn.commit()
    cursor.close()
    print(f"   v {n:,} users inserted")


def seed_products(conn, n=NUM_PRODUCTS):
    print(f"\n[2/4] Seeding {n:,} products...")
    cursor = conn.cursor()
    batch = []
    for i in tqdm(range(n), unit="rows"):
        batch.append((
            fake.catch_phrase()[:255],
            random.choice(CATEGORIES),
            round(random.uniform(5.0, 999.99), 2),
            random.randint(0, 10_000),
            fake.date_time_between(start_date="-2y", end_date="now"),
        ))
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(
                "INSERT INTO products (name, category, price, stock_count, created_at) VALUES (%s,%s,%s,%s,%s)",
                batch,
            )
            conn.commit()
            batch.clear()
    if batch:
        cursor.executemany(
            "INSERT INTO products (name, category, price, stock_count, created_at) VALUES (%s,%s,%s,%s,%s)",
            batch,
        )
        conn.commit()
    cursor.close()
    print(f"   v {n:,} products inserted")


def seed_orders(conn, n=NUM_ORDERS):
    print(f"\n[3/4] Seeding {n:,} orders (main load)...")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users ORDER BY RAND() LIMIT 10000")
    user_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall()
    batch = []
    for i in tqdm(range(n), unit="rows"):
        product_id, price = random.choice(products)
        qty = random.randint(1, 5)
        batch.append((
            random.choice(user_ids),
            product_id,
            qty,
            round(price * qty, 2),
            random.choice(STATUSES),
            fake.date_time_between(start_date="-2y", end_date="now"),
        ))
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(
                "INSERT INTO orders (user_id, product_id, quantity, total_price, status, created_at) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                batch,
            )
            conn.commit()
            batch.clear()
    if batch:
        cursor.executemany(
            "INSERT INTO orders (user_id, product_id, quantity, total_price, status, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            batch,
        )
        conn.commit()
    cursor.close()
    print(f"   v {n:,} orders inserted")


def seed_events(conn, n=NUM_EVENTS):
    print(f"\n[4/4] Seeding {n:,} clickstream events...")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users LIMIT 20000")
    user_ids = [r[0] for r in cursor.fetchall()]
    batch = []
    for i in tqdm(range(n), unit="rows"):
        batch.append((
            random.choice(user_ids),
            random.choice(EVENT_TYPES),
            "/" + fake.uri_path()[:250],
            fake.date_time_between(start_date="-1y", end_date="now"),
        ))
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(
                "INSERT INTO events (user_id, event_type, page, created_at) VALUES (%s,%s,%s,%s)",
                batch,
            )
            conn.commit()
            batch.clear()
    if batch:
        cursor.executemany(
            "INSERT INTO events (user_id, event_type, page, created_at) VALUES (%s,%s,%s,%s)",
            batch,
        )
        conn.commit()
    cursor.close()
    print(f"   v {n:,} events inserted")


def print_summary(conn):
    cursor = conn.cursor()
    tables = ["users","products","orders","events"]
    print("\n--- Row Count Summary ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:<12} {count:>10,} rows")
    cursor.close()


if __name__ == "__main__":
    start = time.time()
    print("MySQL Load Simulator - Data Generator")
    conn = get_connection()
    try:
        seed_users(conn)
        seed_products(conn)
        seed_orders(conn)
        seed_events(conn)
        print_summary(conn)
    finally:
        conn.close()
    print(f"Data generation complete in {time.time() - start:.1f}s")
