-- Star schema for APRA class-of-business performance data (SQLite)

DROP TABLE IF EXISTS fact_cob_metric;
DROP TABLE IF EXISTS dim_quarter;
DROP TABLE IF EXISTS dim_class;
DROP TABLE IF EXISTS dim_state;
DROP TABLE IF EXISTS dim_metric;

-- One row per reporting quarter
CREATE TABLE dim_quarter (
    quarter_id       INTEGER PRIMARY KEY,  -- e.g. 20260630
    period_end       TEXT    NOT NULL,     -- ISO date 'YYYY-MM-DD'
    calendar_year    INTEGER NOT NULL,
    calendar_quarter INTEGER NOT NULL,     -- 1 to 4
    financial_year   TEXT    NOT NULL,     -- Australian FY ending 30 June, e.g. 'FY2026'
    quarter_label    TEXT    NOT NULL      -- e.g. 'Jun 2026'
);

-- One row per class of business
CREATE TABLE dim_class (
    class_id          INTEGER PRIMARY KEY,
    class_of_business TEXT NOT NULL UNIQUE,
    class_category    TEXT NOT NULL,       -- e.g. 'Short-tail property'
    class_group       TEXT NOT NULL        -- 'Direct insurance' or 'Inwards reinsurance'
);

-- One row per state/territory, plus 'National'
CREATE TABLE dim_state (
    state_id   INTEGER PRIMARY KEY,
    state_name TEXT NOT NULL UNIQUE,
    state_code TEXT NOT NULL               -- e.g. 'WA'; 'AUS' for National
);

-- One row per metric
CREATE TABLE dim_metric (
    metric_id   INTEGER PRIMARY KEY,
    metric_name TEXT NOT NULL UNIQUE,      -- e.g. 'insurance_revenue'
    unit        TEXT NOT NULL              -- 'AUD' or 'count'
);

-- One row per quarter + class + state + metric
CREATE TABLE fact_cob_metric (
    quarter_id INTEGER NOT NULL REFERENCES dim_quarter (quarter_id),
    class_id   INTEGER NOT NULL REFERENCES dim_class (class_id),
    state_id   INTEGER NOT NULL REFERENCES dim_state (state_id),
    metric_id  INTEGER NOT NULL REFERENCES dim_metric (metric_id),
    value      REAL,                       -- NULL when masked by APRA
    is_masked  INTEGER NOT NULL CHECK (is_masked IN (0, 1)),
    PRIMARY KEY (quarter_id, class_id, state_id, metric_id)
);