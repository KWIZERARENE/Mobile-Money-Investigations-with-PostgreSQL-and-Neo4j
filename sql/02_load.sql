-- ============================================================================
-- 02_load.sql: Bulk Data Loading for Mobile Money PostgreSQL Database
-- ============================================================================
-- Database: mobile_money
-- Timezone: Africa/Kigali (CAT, UTC+02:00)
-- 
-- Execute inside psql connected to mobile_money:
--   psql -U postgres -d mobile_money -f sql/02_load.sql
--
-- NOTE: If running psql from a different working directory, ensure the relative
-- paths to the data CSVs are correct or use absolute paths.
-- ============================================================================

\timing on

-- 1. Load customers (228,000 rows)
\copy customers (customer_id, region) FROM 'data/customers.csv' WITH (FORMAT csv, HEADER true);

-- 2. Load devices (228,600 rows)
\copy devices (device_id, access_type) FROM 'data/devices.csv' WITH (FORMAT csv, HEADER true);

-- 3. Load accounts (248,000 rows)
\copy accounts (account_id, customer_id, role) FROM 'data/accounts.csv' WITH (FORMAT csv, HEADER true);

-- 4. Load account_devices observations (285,600 rows)
\copy account_devices (account_id, device_id, first_day, last_day, observations) FROM 'data/account_devices.csv' WITH (FORMAT csv, HEADER true);

-- 5. Load transfers (20,003,300 rows)
\copy transfers (transfer_id, sender_id, receiver_id, occurred_at, amount_rwf) FROM 'data/transfers.csv' WITH (FORMAT csv, HEADER true);

\timing off
