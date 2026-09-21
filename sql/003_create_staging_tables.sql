-- RFAW: Staging tables for raw ingested data

-- BNR Interest Rates raw staging
CREATE TABLE IF NOT EXISTS staging.bnr_interest_rates_raw (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) DEFAULT 'BNR-IRS-001',
    year                INTEGER NOT NULL,
    period_label        VARCHAR(50),
    indicator_name      VARCHAR(200) NOT NULL,
    indicator_value     NUMERIC,
    unit                VARCHAR(20) DEFAULT 'percent',
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    raw_row_data        TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- World Bank macro raw staging
CREATE TABLE IF NOT EXISTS staging.world_bank_macro_raw (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) DEFAULT 'WB-MACRO-001',
    country_code        VARCHAR(10) DEFAULT 'RWA',
    country_name        VARCHAR(100) DEFAULT 'Rwanda',
    indicator_code      VARCHAR(100) NOT NULL,
    indicator_name      VARCHAR(300) NOT NULL,
    year                INTEGER NOT NULL,
    value               NUMERIC,
    unit                VARCHAR(50),
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BNR exchange rates raw staging
CREATE TABLE IF NOT EXISTS staging.bnr_exchange_rates_raw (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) DEFAULT 'BNR-FX-001',
    date                DATE NOT NULL,
    currency_pair       VARCHAR(20) NOT NULL,
    rate_type           VARCHAR(50),
    buying_rate         NUMERIC,
    selling_rate        NUMERIC,
    mid_rate            NUMERIC,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bank-level disclosures raw staging
CREATE TABLE IF NOT EXISTS staging.bank_disclosures_raw (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50),
    bank_name           VARCHAR(200) NOT NULL,
    reporting_period    VARCHAR(50) NOT NULL,
    report_date         DATE,
    report_scope        VARCHAR(50),
    indicator_name      VARCHAR(200) NOT NULL,
    indicator_value     NUMERIC,
    unit                VARCHAR(50),
    currency            VARCHAR(20),
    source_url          TEXT,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
