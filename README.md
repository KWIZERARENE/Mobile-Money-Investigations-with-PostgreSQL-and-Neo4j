# Mobile Money Investigations with PostgreSQL and Neo4j
## Advanced Big Data Analytics — Project 2 / Assignment II
### Adventist University of Central Africa (AUCA)
#### Master of Science in Big Data Analytics

A comprehensive comparative evaluation of **PostgreSQL 18.6** and **Neo4j 2026.05.0** across data capture, relational vs. graph schema modeling, routine reporting, multi-hop forensic graph traversals, execution plan optimization, and multi-client concurrent scalability over **20,003,300 financial transfers** (231.48 Billion RWF) in Rwanda for September 2026.

All timestamps and queries operate on **Central Africa Time (CAT, Africa/Kigali, UTC+02:00)**.

---

### Group 4 Members
| No. | Full Name | Student ID | AUCA Institutional Email |
|:---:|:---|:---:|:---|
| 1 | **Amie Marie Flora Dushimumukiza** | 101405 | dushimumukiza.flora@auca.ac.rw |
| 2 | **Kwizera Rene** | 101379 | rene.kwizera@auca.ac.rw |
| 3 | **Grace Teta** | 101378 | grace.teta@auca.ac.rw |

**Lecturer:** Temitope Oguntade  
**Academic Year:** 2026  
**Due Date:** 26 October 2026 at 11:59 PM CAT  
**Submission Date:** 25 October 2026  
**GitHub Repository:** [KWIZERARENE/Mobile-Money-Investigations-with-PostgreSQL-and-Neo4j](https://github.com/KWIZERARENE/Mobile-Money-Investigations-with-PostgreSQL-and-Neo4j)

---

## Repository Structure

```
c:\assignement\
├── README.md                                  # Complete project documentation and runbook
├── requirements.txt                           # Python package dependencies
├── setup_env.ps1                              # PowerShell virtual environment setup helper
│
├── report/                                    # Final project report deliverables
│   ├── Assignment II Group Report GROUP 4.docx # Comprehensive 60-page Word report (.docx)
│   └── Assignment II Group Report GROUP 4.pdf  # Final compiled PDF report with embedded screenshots
│
├── code/                                      # Production pipeline, analytical & reporting scripts (25 files)
│   ├── mobile_money_generator.py              # Unchanged synthetic generator (SHA-256 verified)
│   ├── view.py                                # Milestone 1: Preview first 10 rows per stream
│   ├── capture.py                             # Milestone 1: Progressive CSV streaming & audit log
│   ├── prepare_import.py                      # Milestone 3: Generate Neo4j typed import CSVs
│   ├── db.py                                  # Central database connection manager
│   ├── timeutil.py                            # CAT epoch timestamp boundary helper
│   ├── cases.py                               # Review account configurations for Sets A–F
│   ├── queries.py                             # Parameterized SQL and Cypher query pairs (Q1–Q7)
│   ├── verify_counts.py                       # Database entity and relationship count validation
│   ├── independent_check.py                   # Milestone 6: Independent CSV validation in Python
│   ├── run_all.py                             # Milestone 6: 61-case cross-engine test runner
│   ├── save_all.py                            # Milestone 6: Full results exporter (results/full/*.json)
│   ├── q7_paths.py                            # Milestone 5: Q7 path direction and role validator
│   ├── q7_v2.py                               # Milestone 6: Benchmark comparing Q7 v1 vs q7_v2
│   ├── bench.py                               # Milestone 6: 21-case warm-cache performance timer
│   ├── report_timing.py                       # Milestone 6: Summarizes raw timing into CSV
│   ├── plans.py                               # Milestone 6: Extracts EXPLAIN and PROFILE plans
│   ├── conc.py                                # Milestone 7: Multi-process concurrency load tester
│   ├── plot_conc.py                           # Milestone 7: Aggregates concurrency and plots charts
│   ├── evidence.py                            # Milestone 8: Gathers forensic evidence for Sets A–F
│   ├── diagrams.py                            # Milestone 8: Generates Set C cycle & device diagrams
│   ├── build_report_doc.py                    # Report Builder: Compiles formatted Word report (.docx)
│   ├── convert_to_pdf.ps1                     # PDF Exporter: Converts Word report to PDF via COM
│   ├── build_guide_doc.py                     # Guide Builder: Compiles line-by-line explanation doc
│   └── convert_guide_to_pdf.ps1               # Guide Exporter: Converts explanation doc to PDF
│
├── sql/                                       # PostgreSQL scripts in execution order (01 to 05)
│   ├── 01_schema.sql                          # Table definitions, primary keys, and domain checks
│   ├── 02_load.sql                            # High-speed \copy bulk loading in dependency order
│   ├── 03_constraints_indexes.sql             # Foreign keys, covering B-tree indexes, and BRIN index
│   ├── 04_verify.sql                          # Database verification, roles, sizes, and audit checks
│   └── 05_q7_v2.sql                          # Optimized iterative BFS shortest-path function
│
├── results/                                   # Experimental results, summaries, plans, and diagrams
│   ├── capture_audit.json                     # Master audit totals from streaming capture
│   ├── summary.csv                            # 61-case cross-engine verification summary
│   ├── all_answers.txt                        # Formatted query outputs for all 61 cases
│   ├── timing_summary.csv                     # 21-case median benchmark timing comparison
│   ├── concurrency_final.csv                  # Concurrency throughput and latency summary
│   ├── concurrency_plot.png                   # Concurrency scaling chart (throughput & p95)
│   ├── diagram_cycle_C.png                    # Set C 6-transfer circular payment cycle diagram
│   ├── diagram_devices_C.png                  # Set C device co-location bipartite network diagram
│   ├── generator_hash.txt                     # SHA-256 integrity verification of generator
│   ├── pg_load_time.txt                       # Measured PostgreSQL load duration (52.8 s)
│   ├── pg_index_time.txt                      # Measured PostgreSQL index setup duration (58.4 s)
│   ├── import_log.txt                         # Neo4j offline admin import statistics (50.4 s)
│   ├── neo4j.conf.snapshot                    # Snapshot of Neo4j DBMS memory configuration
│   ├── full/                                  # Complete JSON outputs for all 61 cases
│   ├── logs/                                  # Raw console outputs and execution traces
│   └── smoke_tests/                           # Intermediate exploratory test logs
│
├── screenshots/                               # 45 verified execution screenshots with taskbar/clock visible
├── data/                                      # Generated CSV files (git-ignored, regenerated locally)
└── archive/                                   # Deprecated scratch scripts from exploratory phases
    └── scratch_code/                          # Archived prototypes (dump_results.py, test_one.py, etc.)
```

---

## Security and Environment Configuration

Passwords and secrets are never committed to this repository. Set them as environment variables in your active shell:

```powershell
$env:PGPASSWORD = "<your-postgres-password>"
$env:NEO4J_PASSWORD = "<your-neo4j-password>"
```

### Python Virtual Environment Setup

```powershell
cd C:\assignement
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Generator Verification

The generator script `mobile_money_generator.py` is preserved strictly unchanged from the assignment release:

```powershell
certutil -hashfile code\mobile_money_generator.py SHA256
```
**Expected Hash:** `2EA0E59D2B7B987D84A3D151BD9D1AD7B3052BFBC25ABF1466C8E94467E9455A`  
**Git Commit:** `5b935ec` (Git blob: `93ca8973736466c6510563c6750b3df8d700aea5`)

---

## End-to-End Execution Runbook

All commands are executed from `C:\assignement\code` unless otherwise noted.

### Phase 1: Data Capture & Verification
```powershell
cd C:\assignement\code

# Preview first 10 rows of each stream (Section 1.2 Step 1)
python view.py

# Stream 20,993,500 records to CSV without holding full stream in memory
python capture.py
```
*Output:* Creates `data/*.csv` and `results/capture_audit.json`.

---

### Phase 2: PostgreSQL Schema, Loading, and Indexing
Ensure the PostgreSQL server is running and the database `mobile_money` is created with timezone `Africa/Kigali`:

```powershell
# 1. Define tables, primary keys, and check constraints
psql -U postgres -d mobile_money -f ..\sql\01_schema.sql

# 2. Bulk load data via \copy in dependency order
psql -U postgres -d mobile_money -f ..\sql\02_load.sql

# 3. Build foreign keys, B-tree covering indexes, and BRIN index
psql -U postgres -d mobile_money -f ..\sql\03_constraints_indexes.sql

# 4. Verify row counts, account roles, and storage sizes
psql -U postgres -d mobile_money -f ..\sql\04_verify.sql

# 5. Create optimized shortest-path function q7_v2
psql -U postgres -d mobile_money -f ..\sql\05_q7_v2.sql
```

---

### Phase 3: Neo4j Offline Import and Schema Constraints
```powershell
# 1. Generate typed CSV import files and derive owns.csv
python prepare_import.py

# 2. Stop Neo4j DBMS service before offline import
neo4j stop

# 3. Execute high-speed admin import
neo4j-admin database import full neo4j `
  --id-type=integer `
  --nodes=Customer="customers_import.csv" `
  --nodes=Device="devices_import.csv" `
  --nodes=Account="accounts_import.csv" `
  --relationships=OWNS="owns_import.csv" `
  --relationships=USED_DEVICE="account_devices_import.csv" `
  --relationships=TRANSFER="transfers_import.csv"

# 4. Start Neo4j DBMS service
neo4j start

# 5. Create constraints and TRANSFER range index via cypher-shell
cypher-shell -u neo4j -p $env:NEO4J_PASSWORD "CREATE CONSTRAINT c_cust FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;"
cypher-shell -u neo4j -p $env:NEO4J_PASSWORD "CREATE CONSTRAINT c_acc FOR (a:Account) REQUIRE a.account_id IS UNIQUE;"
cypher-shell -u neo4j -p $env:NEO4J_PASSWORD "CREATE CONSTRAINT c_dev FOR (d:Device) REQUIRE d.device_id IS UNIQUE;"
cypher-shell -u neo4j -p $env:NEO4J_PASSWORD "CREATE INDEX idx_tr_time FOR ()-[t:TRANSFER]->() ON (t.occurred_at);"
```

---

### Phase 4 & 5: Correctness and Verification Checks (61 Cases)
Both database services must be running.

```powershell
# Verify row counts and audit reconciliation in both engines
python verify_counts.py

# Perform independent verification directly from raw CSV files in plain Python
python independent_check.py

# Run all 61 cases and check exact numerical agreement
python run_all.py

# Save complete JSON outputs to results/full/ and generate summary.csv & all_answers.txt
python save_all.py

# Validate Q7 shortest transfer routes (existence, direction, person roles)
python q7_paths.py
```

---

### Phase 6: Performance Benchmarking and Execution Plans
Run benchmarks **one engine at a time** to eliminate system resource contention.

```powershell
# 1. Benchmark PostgreSQL (3 warm-ups + 5 measured runs across 21 queries)
python bench.py pg

# 2. Benchmark Neo4j (3 warm-ups + 5 measured runs across 21 queries)
python bench.py neo

# 3. Generate consolidated benchmark timing summary table
python report_timing.py

# 4. Extract EXPLAIN (ANALYZE, BUFFERS) and PROFILE execution plans
python plans.py

# 5. Compare SQL v1 against optimized function q7_v2
python q7_v2.py
```

---

### Phase 7: Concurrency Stress-Testing (1, 4, 8, 16 Clients)
Simulate multi-client querying under a 15-second deadline with Barrier synchronization:

```powershell
# 1. Run PostgreSQL concurrency load test (using q7_v2)
python conc.py --engine pg --q7 v2

# 2. Run Neo4j concurrency load test
python conc.py --engine neo

# 3. Aggregate 3 repetitions into concurrency_final.csv and plot scaling curves
python plot_conc.py
```

---

### Phase 8: Decisions and Diagram Generation
```powershell
# Collect structured forensic evidence for suspect pairs A/D, B/E, and C/F
python evidence.py

# Generate circular transfer cycle and device sharing diagrams for Set C
python diagrams.py
```
*Output:* Creates `results/diagram_cycle_C.png` and `results/diagram_devices_C.png`.

---

### Phase 9: Final Submission Verification
```powershell
# 1. Re-run 61-case cross-engine test suite to confirm 100% agreement
python run_all.py

# 2. Stop both database services and verify stopped status
net stop postgresql-x64-18
neo4j stop
```

---

### Phase 10: Report Generation and PDF Compilation (Deliverables)
The final submission report is automatically built and compiled directly from raw execution results, markdown text, and high-resolution screenshots:

```powershell
cd C:\assignement\code

# 1. Compile the comprehensive Word report (.docx) with embedded figures & styled tables
python build_report_doc.py

# 2. Export Word document to standalone publication PDF via Microsoft Word COM automation
powershell -ExecutionPolicy Bypass -File convert_to_pdf.ps1
```
*Output:* Compiles `report/Assignment II Group Report GROUP 4.docx` and `report/Assignment II Group Report GROUP 4.pdf`.

---

## Deliverables Summary

* **Final PDF Report:** [`report/Assignment II Group Report GROUP 4.pdf`](report/Assignment%20II%20Group%20Report%20GROUP%204.pdf) (Comprehensive 60-page technical report with embedded screenshots)
* **Final Word Document:** [`report/Assignment II Group Report GROUP 4.docx`](report/Assignment%20II%20Group%20Report%20GROUP%204.docx)
* **Code Submissions:** Complete production pipeline in [`code/`](code/) and SQL scripts in [`sql/`](sql/)
* **Execution Screenshots:** 45 numbered, timestamp-verified screenshots in [`screenshots/`](screenshots/)
* **Benchmarking Artifacts:** [`results/summary.csv`](results/summary.csv), [`results/timing_summary.csv`](results/timing_summary.csv), [`results/concurrency_final.csv`](results/concurrency_final.csv)
