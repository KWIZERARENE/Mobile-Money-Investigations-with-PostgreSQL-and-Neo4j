# Project 2: Mobile Money Investigations (PostgreSQL and Neo4j)

Compares PostgreSQL 18 and Neo4j (Desktop DBMS 2026.05.0) on seven investigation queries (Q1 to Q7) over the September 2026 mobile money data (20,003,300 transfers).
All times are CAT (Africa/Kigali). Windows, PowerShell, Python 3 with a virtual environment.

## Secrets
Passwords are never stored in this repository. Set them in the shell before running anything:

    $env:PGPASSWORD = "<your-postgres-password>"
    $env:NEO4J_PASSWORD = "<your-neo4j-password>"

Do not commit the generated CSV files or the database stores.

## Setup
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install psycopg[binary] neo4j matplotlib

`mobile_money_generator.py` is unchanged; its hash is recorded in `results\generator_hash.txt` (if you saved it there).

## Run order (from C:\assignement\code)
1. [PostgreSQL: create database `mobile_money` with timezone Africa/Kigali, load the data and build the indexes (your Phase 2 commands)]
2. [Neo4j: `python prepare_import.py`, then `neo4j-admin database import full ... --id-type=...` (your Phase 3 commands), then create indexes]
3. `python verify_counts.py`      row counts, both engines
4. `python independent_check.py`  independent check of the results
5. `python run_all.py`            run the 61 cases
6. `python save_all.py`           save full results to results\full and compare engines (both services running)
7. `python q7_paths.py`           Q7 path details
8. `python bench.py pg` ; `python bench.py neo`   3 warm-ups and 5 measured runs (run one database at a time)
9. `python report_timing.py`      timing summary
10. `python plans.py`             execution plans
11. `python conc.py --engine pg --q7 v2` ; `python conc.py --engine neo`   concurrency (1, 4, 8, 16 clients)
12. `python plot_conc.py`         concurrency table and chart
13. `python evidence.py`          evidence for sets A to F (PostgreSQL running)
14. `python diagrams.py`          cycle and device diagrams for set C

Q7 on PostgreSQL uses the function `q7_v2` (level-by-level search); create it in pgAdmin before steps 5 to 11.

## Output
All results are written to `C:\assignement\results`.
