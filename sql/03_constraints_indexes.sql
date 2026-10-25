ALTER TABLE accounts ADD CONSTRAINT fk_accounts_customer FOREIGN KEY (customer_id) REFERENCES customers (customer_id);
ALTER TABLE account_devices ADD CONSTRAINT fk_ad_account FOREIGN KEY (account_id) REFERENCES accounts (account_id);
ALTER TABLE account_devices ADD CONSTRAINT fk_ad_device FOREIGN KEY (device_id) REFERENCES devices (device_id);
ALTER TABLE transfers ADD CONSTRAINT fk_tr_sender FOREIGN KEY (sender_id) REFERENCES accounts (account_id);
ALTER TABLE transfers ADD CONSTRAINT fk_tr_receiver FOREIGN KEY (receiver_id) REFERENCES accounts (account_id);

CREATE INDEX idx_accounts_cust ON accounts (customer_id, account_id);
CREATE INDEX idx_ad_device ON account_devices (device_id, account_id);
CREATE INDEX idx_tr_sender ON transfers (sender_id, occurred_at) INCLUDE (receiver_id, amount_rwf, transfer_id);
CREATE INDEX idx_tr_receiver ON transfers (receiver_id, occurred_at) INCLUDE (sender_id, amount_rwf, transfer_id);
CREATE INDEX idx_tr_time_brin ON transfers USING brin (occurred_at);
ANALYZE;
