-- RFAW: Analytical mart tables

-- Interest rates fact table
CREATE TABLE IF NOT EXISTS mart.fact_interest_rates (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL,
    indicator_id        VARCHAR(100) NOT NULL,
    date                DATE NOT NULL,
    frequency           VARCHAR(20) NOT NULL,
    indicator_name      VARCHAR(200) NOT NULL,
    value               NUMERIC NOT NULL,
    unit                VARCHAR(20) DEFAULT 'percent',
    evidence_classification VARCHAR(50) DEFAULT 'VERIFIED_PRIMARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    transformation_notes TEXT,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    UNIQUE(source_id, indicator_id, date, frequency)
);

-- Macro indicators fact table
CREATE TABLE IF NOT EXISTS mart.fact_macro_indicators (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL,
    indicator_id        VARCHAR(100) NOT NULL,
    date                DATE NOT NULL,
    frequency           VARCHAR(20) NOT NULL,
    indicator_name      VARCHAR(300) NOT NULL,
    value               NUMERIC NOT NULL,
    unit                VARCHAR(50),
    evidence_classification VARCHAR(50) DEFAULT 'VERIFIED_SECONDARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    transformation_notes TEXT,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    UNIQUE(source_id, indicator_id, date, frequency)
);

-- Banking sector aggregates fact table
CREATE TABLE IF NOT EXISTS mart.fact_banking_sector (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL,
    indicator_id        VARCHAR(100) NOT NULL,
    date                DATE NOT NULL,
    frequency           VARCHAR(20) NOT NULL,
    indicator_name      VARCHAR(200) NOT NULL,
    value               NUMERIC NOT NULL,
    unit                VARCHAR(50),
    currency            VARCHAR(20),
    evidence_classification VARCHAR(50) DEFAULT 'VERIFIED_PRIMARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    transformation_notes TEXT,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    UNIQUE(source_id, indicator_id, date, frequency)
);

-- Derived metrics fact table (clearly labeled as derived)
CREATE TABLE IF NOT EXISTS mart.fact_derived_metrics (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL,
    indicator_id        VARCHAR(100) NOT NULL,
    date                DATE NOT NULL,
    frequency           VARCHAR(20) NOT NULL,
    indicator_name      VARCHAR(200) NOT NULL,
    value               NUMERIC NOT NULL,
    unit                VARCHAR(50),
    evidence_classification VARCHAR(50) DEFAULT 'DERIVED',
    is_observed         BOOLEAN DEFAULT FALSE,
    is_derived          BOOLEAN DEFAULT TRUE,
    transformation_notes TEXT,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    UNIQUE(source_id, indicator_id, date, frequency)
);

-- Exchange rates fact table
CREATE TABLE IF NOT EXISTS mart.fact_exchange_rates (
    id                  SERIAL PRIMARY KEY,
    source_id           VARCHAR(50) NOT NULL,
    currency_pair       VARCHAR(20) NOT NULL,
    date                DATE NOT NULL,
    frequency           VARCHAR(20) NOT NULL,
    rate_type           VARCHAR(50),
    value               NUMERIC NOT NULL,
    unit                VARCHAR(50) DEFAULT 'RWF per unit foreign',
    evidence_classification VARCHAR(50) DEFAULT 'VERIFIED_PRIMARY',
    is_observed         BOOLEAN DEFAULT TRUE,
    is_derived          BOOLEAN DEFAULT FALSE,
    retrieval_date      DATE DEFAULT CURRENT_DATE,
    UNIQUE(source_id, currency_pair, date, frequency, rate_type)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_interest_rates_date ON mart.fact_interest_rates(date);
CREATE INDEX IF NOT EXISTS idx_interest_rates_indicator ON mart.fact_interest_rates(indicator_id);
CREATE INDEX IF NOT EXISTS idx_macro_date ON mart.fact_macro_indicators(date);
CREATE INDEX IF NOT EXISTS idx_macro_indicator ON mart.fact_macro_indicators(indicator_id);
CREATE INDEX IF NOT EXISTS idx_banking_date ON mart.fact_banking_sector(date);
CREATE INDEX IF NOT EXISTS idx_banking_indicator ON mart.fact_banking_sector(indicator_id);
CREATE INDEX IF NOT EXISTS idx_fx_date ON mart.fact_exchange_rates(date);
CREATE INDEX IF NOT EXISTS idx_fx_pair ON mart.fact_exchange_rates(currency_pair);
