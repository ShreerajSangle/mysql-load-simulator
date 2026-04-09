"""
load_simulator.py
-----------------
Simulates concurrent production traffic patterns against the MySQL database.
Runs multiple threads mimicking real user activity (reads + writes).

Usage:
    python src/load_simulator.py
"""

import os
import random
import threading
import time
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "load_simulator"),
    "user":     os.getenv("MYSQL_USER", "labuser"),
    "password": os.getenv("MYSQL_PASSWORD", "labpassword"),
}

THREADS    = 10
DURATION_S = 30
STATUSES   = ["pending","processing","shipped","delivered","cancelled"]

results    = {"reads": 0, "writes": 0, "errors": 0}
lock       = threading.Lock()
stop_event = threading.Event()


def worker(thread_id):
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    while not stop_event.is_set():
        try:
            action = random.choices(["read","write"], weights=[0.8, 0.2])[0]
            if action == "read":
                user_id = random.randint(1, 50_000)
                cursor.execute(
                    "SELECT order_id, status, total_price FROM orders WHERE user_id=%s LIMIT 10",
                    (user_id,),
                )
                cursor.fetchall()
                with lock:
                    results["reads"] += 1
            else:
                status   = random.choice(STATUSES)
                order_id = random.randint(1, 500_000)
                cursor.execute(
                    "UPDATE orders SET status=%s WHERE order_id=%s",
                    (status, order_id),
                )
                conn.commit()
                with lock:
                    results["writes"] += 1
        except Exception:
            with lock:
                results["errors"] += 1
    cursor.close()
    conn.close()


if __name__ == "__main__":
    print(f"MySQL Load Simulator - Traffic Engine")
    print(f"Threads: {THREADS}  Duration: {DURATION_S}s")
    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(THREADS)]
    for t in threads:
        t.start()
    start = time.time()
    while time.time() - start < DURATION_S:
        elapsed = time.time() - start
        rps = (results["reads"] + results["writes"]) / max(elapsed, 0.001)
        print(f"\r  elapsed={elapsed:.1f}s | reads={results['reads']:,} | writes={results['writes']:,} | errors={results['errors']} | ~{rps:.0f} ops/s", end="", flush=True)
        time.sleep(0.5)
    stop_event.set()
    for t in threads:
        t.join(timeout=2)
    print(f"\n\nTotal Reads : {results['reads']:,}")
    print(f"Total Writes: {results['writes']:,}")
    print(f"Errors      : {results['errors']}")
    print(f"Avg Ops/s   : {(results['reads'] + results['writes']) / DURATION_S:.0f}")
    print("Load simulation complete")
