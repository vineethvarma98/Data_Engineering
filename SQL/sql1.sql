-- orginal transactional table
CREATE TABLE alerts (
    alert_id        BIGINT PRIMARY KEY,
    title           VARCHAR(255),
    severity        VARCHAR(20),
    status          VARCHAR(20),
    source_system   VARCHAR(100),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    resolved_at     TIMESTAMP
);



CREATE TABLE fact_alerts (
    alert_id        BIGINT PRIMARY KEY,
    created_date    DATE,
    resolved_date   DATE,
    severity_id     INT,
    status_id       INT,
    source_id       INT,
    resolution_time_minutes INT,
    updated_timestamp  timestamp
);

CREATE TABLE dim_severity (
    severity_id INT PRIMARY KEY,
    severity_name VARCHAR(20),
    updated_time timestamp
);

CREATE TABLE dim_status (
    status_id INT PRIMARY KEY,
    status_name VARCHAR(20),
    updated_timestamp timestamp
);

CREATE TABLE dim_source (
    source_id INT PRIMARY KEY,
    source_name VARCHAR(100),
    updated_time timestamp
);