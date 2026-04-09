"""
reporter.py
-----------
Reads benchmark_log table and generates a standalone HTML performance report
comparing before vs. after optimization results.

Usage:
    python src/reporter.py
Output:
    docs/benchmark_report.html
"""

import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "load_simulator"),
    "user":     os.getenv("MYSQL_USER", "labuser"),
    "password": os.getenv("MYSQL_PASSWORD", "labpassword"),
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "benchmark_report.html")


def fetch_results(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT phase, query_name,
               AVG(avg_ms) AS avg_ms,
               MIN(min_ms) AS min_ms,
               MAX(max_ms) AS max_ms
        FROM benchmark_log
        GROUP BY phase, query_name
        ORDER BY query_name, phase
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def build_comparison(rows):
    data = {}
    for r in rows:
        qname = r["query_name"]
        phase = r["phase"]
        if qname not in data:
            data[qname] = {}
        data[qname][phase] = r
    return data


def improvement_pct(before, after):
    if before and before > 0:
        return round((before - after) / before * 100, 1)
    return 0


def render_html(data):
    rows_html = ""
    for qname, phases in sorted(data.items()):
        before = phases.get("before", {})
        after  = phases.get("after", {})
        b_avg  = float(before.get("avg_ms", 0) or 0)
        a_avg  = float(after.get("avg_ms",  0) or 0)
        pct    = improvement_pct(b_avg, a_avg)
        color  = "#22c55e" if pct > 0 else "#ef4444"
        rows_html += f"""
        <tr>
          <td>{qname}</td>
          <td>{b_avg:.2f}</td>
          <td>{a_avg:.2f}</td>
          <td style="color:{color};font-weight:600">{pct}%</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MySQL Benchmark Report</title>
  <style>
    body  {{ font-family: 'Segoe UI', sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:2rem; }}
    h1    {{ color:#38bdf8; }}
    p     {{ color:#94a3b8; }}
    table {{ border-collapse:collapse; width:100%; margin-top:1.5rem; }}
    th    {{ background:#1e293b; color:#7dd3fc; padding:0.75rem 1rem; text-align:left; }}
    td    {{ padding:0.75rem 1rem; border-bottom:1px solid #1e293b; }}
    tr:hover td {{ background:#1e293b; }}
    .badge {{ display:inline-block; padding:0.2rem 0.6rem; border-radius:9999px;
              background:#0f4c75; color:#7dd3fc; font-size:0.8rem; }}
  </style>
</head>
<body>
  <h1>MySQL Load Simulator &mdash; Benchmark Report</h1>
  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  <p><span class="badge">Self-Learning Project</span> &nbsp; ShreerajSangle / mysql-load-simulator</p>
  <table>
    <thead>
      <tr>
        <th>Query</th>
        <th>Avg Before (ms)</th>
        <th>Avg After (ms)</th>
        <th>Improvement</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</body>
</html>"""


if __name__ == "__main__":
    conn = mysql.connector.connect(**DB_CONFIG)
    rows = fetch_results(conn)
    conn.close()

    if not rows:
        print("No benchmark data found. Run query_bench.py --mode before and --mode after first.")
    else:
        data = build_comparison(rows)
        html = render_html(data)
        out  = os.path.abspath(OUTPUT_FILE)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(html)
        print(f"Report saved to: {out}")
