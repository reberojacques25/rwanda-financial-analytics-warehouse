-- RFAW: Create database schemas
-- Run this first to set up the schema structure

CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS reference;

COMMENT ON SCHEMA metadata IS 'Source catalogs, provenance, and data quality metadata';
COMMENT ON SCHEMA staging IS 'Raw ingested data before transformation';
COMMENT ON SCHEMA mart IS 'Cleaned, transformed analytical tables';
COMMENT ON SCHEMA reference IS 'Reference/dimension tables (indicators, units, etc.)';
