-- RFAW: Metadata tables for provenance and source catalog

-- Sources registry
CREATE TABLE IF NOT EXISTS metadata.sources (
    source_id           VARCHAR(50) PRIMARY KEY,
    source_name         VARCHAR(200),
    source_organization VARCHAR(200) NOT NULL,
    dataset_name        VARCHAR(200),
    source_type         VARCHAR(100),
    source_url          TEXT NOT NULL,
    landing_page        TEXT,
    source_format       VARCHAR(50),
    retrieval_date      DATE NOT NULL,
    publication_date    VARCHAR(20),
    frequency           VARCHAR(50),
    geographic_scope    VARCHAR(100),
    geographic_coverage VARCHAR(100),
    unit                VARCHAR(100),
    currency            VARCHAR(20),
    format              VARCHAR(50),
    access_type         VARCHAR(50),
    registration_required BOOLEAN DEFAULT FALSE,
    api_available       BOOLEAN DEFAULT FALSE,
    api_access          VARCHAR(50),
    api_endpoint        TEXT,
    license             TEXT,
    redistribution_status VARCHAR(50) DEFAULT 'unclear',
    evidence_classification VARCHAR(50) NOT NULL DEFAULT 'VERIFIED_PRIMARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    ingestion_status    VARCHAR(50) DEFAULT 'CATALOGED_PENDING_EXTRACTION',
    is_active           BOOLEAN DEFAULT TRUE,
    date_coverage       VARCHAR(100),
    historical_completeness TEXT,
    transformations_applied TEXT,
    methodology_notes   TEXT,
    limitations         TEXT,
    variables           TEXT,
    intended_use        TEXT,
    warehouse_use       TEXT,
    priority            INTEGER DEFAULT 99,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Source files registry (tracks downloaded/processed files)
CREATE TABLE IF NOT EXISTS metadata.source_files (
    file_id             SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL REFERENCES metadata.sources(source_id),
    file_name           VARCHAR(500) NOT NULL,
    file_url            TEXT,
    file_format         VARCHAR(20),
    file_size_bytes     BIGINT,
    download_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    file_hash           VARCHAR(128),
    processing_status   VARCHAR(50) DEFAULT 'pending',
    notes               TEXT
);

-- Indicators dictionary
CREATE TABLE IF NOT EXISTS metadata.indicators (
    indicator_id        VARCHAR(100) PRIMARY KEY,
    indicator_name      VARCHAR(200) NOT NULL,
    indicator_category  VARCHAR(100),
    unit                VARCHAR(50),
    frequency           VARCHAR(50),
    description         TEXT,
    source_id           VARCHAR(50) REFERENCES metadata.sources(source_id),
    evidence_classification VARCHAR(50) DEFAULT 'VERIFIED_PRIMARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    derivation_formula  TEXT,
    valid_range_min     NUMERIC,
    valid_range_max     NUMERIC,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data quality results
CREATE TABLE IF NOT EXISTS metadata.data_quality_results (
    check_id            SERIAL PRIMARY KEY,
    check_name          VARCHAR(200) NOT NULL,
    check_type          VARCHAR(100) NOT NULL,
    table_name          VARCHAR(200),
    check_date          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    passed              BOOLEAN NOT NULL,
    failed_records       INTEGER DEFAULT 0,
    total_records        INTEGER DEFAULT 0,
    details             TEXT
);

-- Insert allowed evidence classifications as a comment
COMMENT ON TABLE metadata.sources IS 'Evidence classifications allowed: VERIFIED_PRIMARY, VERIFIED_SECONDARY, DERIVED, ESTIMATED, UNVERIFIED';
