-- Indexed tenant-isolated exception read model (writer runs in trusted ingestion job).
CREATE TABLE IF NOT EXISTS delivery_exceptions (
 tenant_id varchar(64) NOT NULL,
 order_id varchar(64) NOT NULL,
 reason_code varchar(64) NOT NULL,
 promised_date date NOT NULL,
 estimated_delivery date,
 delivered_at date,
 shipment_status varchar(100),
 source_event varchar(250),
 source_updated_at timestamptz,
 refreshed_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY (tenant_id,order_id)
);
CREATE INDEX IF NOT EXISTS idx_delivery_exceptions_tenant_refresh
  ON delivery_exceptions (tenant_id,refreshed_at DESC,order_id);
-- Operators must configure separate runtime READ, ingestion WRITE and migration OWNER roles.
-- Enable database RLS and enforce trusted tenant session context before actual multitenant production.

CREATE TABLE IF NOT EXISTS exception_refresh_state (
 tenant_id varchar(64) PRIMARY KEY,
 refreshed_at timestamptz NOT NULL,
 indexed_count integer NOT NULL CHECK(indexed_count >= 0)
);
