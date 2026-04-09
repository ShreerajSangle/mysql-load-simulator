# MySQL Load Simulator & Query Optimization Lab

A self-learning proof-of-concept project designed to master database performance at scale, simulate production-level MySQL workloads, and study query optimization strategies.

## Project Overview

| Attribute | Details |
|---|---|
| **Duration** | 6 Weeks (Self-Learning) |
| **Tech Stack** | Python, MySQL, Docker, Jira (free tier), Faker, GitHub Actions |
| **Goal** | Simulate production traffic patterns and reduce query latency through indexing & refactoring |
| **Outcome** | ~84% reduction in average query response time |

## Problem Statement

Production MySQL databases often face severe performance degradation under high-volume, concurrent loads. This project replicates a real-world scenario: a 500K-row dataset simulating production traffic, with systematic indexing, query plan analysis, and partitioning applied to identify and resolve bottlenecks.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MySQL Load Simulator                       │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Faker   │──▶│  data_gen.py │──▶│  MySQL Database  │  │
│  │ (Python) │    │  (ETL Load)  │    │  (500K rows)     │  │
│  └──────────┘    └──────────────┘    └──────────────────┘  │
│                                              │               │
│                         ┌────────────────────┘              │
│                         ▼                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Benchmarker  │──▶│  Optimizer   │──▶│  Reporter    │  │
│  │ (query_bench)│    │  (indexes,  │    │  (latency    │  │
│  │              │    │   EXPLAIN)  │    │   CSV/HTML)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
mysql-load-simulator/
├── README.md
├── docker-compose.yml          # MySQL + phpMyAdmin environment
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── src/
│   ├── data_gen.py             # Synthetic data generation (Faker)
│   ├── load_simulator.py       # Production traffic pattern simulation
│   ├── query_bench.py          # Query benchmarking before/after
│   ├── optimizer.py            # Index creation & query refactoring
│   └── reporter.py             # HTML performance report generator
├── sql/
│   ├── schema.sql              # Database schema
│   ├── seed_queries.sql        # Test queries (slow, unoptimized)
│   └── optimized_queries.sql   # Post-optimization queries
└── docs/
    ├── OPTIMIZATION_WIKI.md    # Personal engineering wiki
    └── LEARNINGS.md            # Self-study notes & key findings
```

## Setup & Usage

### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Quick Start

```bash
# 1. Clone & navigate
git clone https://github.com/ShreerajSangle/mysql-load-simulator.git
cd mysql-load-simulator

# 2. Copy env template
cp .env.example .env

# 3. Start MySQL via Docker
docker-compose up -d

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Generate synthetic data (500K rows)
python src/data_gen.py

# 6. Run benchmarks (before optimization)
python src/query_bench.py --mode before

# 7. Apply indexes & optimizations
python src/optimizer.py

# 8. Run benchmarks (after optimization)
python src/query_bench.py --mode after

# 9. Generate HTML report
python src/reporter.py
```

## Key Findings & Optimizations

| Optimization | Latency Before | Latency After | Improvement |
|---|---|---|---|
| Composite Index on `(user_id, created_at)` | 420ms | 38ms | **91%** |
| Covering Index on `(status, created_at)` | 310ms | 62ms | **80%** |
| N+1 Query Fix → JOIN rewrite | 1800ms | 190ms | **89%** |
| Date range index on `created_at` | 650ms | 210ms | **68%** |
| **Overall Average** | **795ms** | **125ms** | **~84%** |

## Self-Learning Methods

- Studied MySQL EXPLAIN plans and execution trees from [MySQL Documentation](https://dev.mysql.com/doc/)
- Explored free-tier [PlanetScale](https://planetscale.com/) for branching workflow simulation
- Tracked all tasks via **Jira free tier** with GitHub connector monitoring pull requests
- Applied learnings from *High Performance MySQL* (O'Reilly) and MySQL Blog
- Documented every optimization in `/docs/OPTIMIZATION_WIKI.md` as a personal engineering wiki

## CI/CD Pipeline

GitHub Actions automatically:
1. Spins up a MySQL 8.0 test container
2. Runs schema scripts
3. Validates all tables exist
4. Lints Python source files with pyflakes

## Skills Demonstrated

`Python` `MySQL` `Docker` `SQL Indexing` `Query Optimization` `ETL` `Faker` `GitHub Actions` `Jira` `Data Engineering` `Performance Benchmarking`

---

*Self-learning project | Shreeraj Sangle | MSc Artificial Intelligence, NCI Dublin*
