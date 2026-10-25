SELECT 'customers' AS tbl, count(*) FROM customers UNION ALL
SELECT 'accounts', count(*) FROM accounts UNION ALL
SELECT 'devices', count(*) FROM devices UNION ALL
SELECT 'account_devices', count(*) FROM account_devices UNION ALL
SELECT 'transfers', count(*) FROM transfers;

SELECT count(*) AS n, min(occurred_at) AS min_t, max(occurred_at) AS max_t, sum(amount_rwf::bigint) AS total_rwf FROM transfers;

SELECT role, count(*) FROM accounts GROUP BY role ORDER BY role;

SELECT conrelid::regclass AS tbl, conname, contype, convalidated FROM pg_constraint WHERE connamespace = 'public'::regnamespace ORDER BY 1, 2;

SELECT tablename, indexname, pg_size_pretty(pg_relation_size(format('%I.%I', schemaname, indexname)::regclass)) AS size FROM pg_indexes WHERE schemaname = 'public' ORDER BY 1, 2;

SELECT relname, round(pg_table_size(oid)/1e9, 3) AS table_gb, round(pg_indexes_size(oid)/1e9, 3) AS index_gb FROM pg_class WHERE relname IN ('customers','accounts','devices','account_devices','transfers') ORDER BY 1;

SELECT round(pg_database_size('mobile_money')/1e9, 3) AS database_gb;






