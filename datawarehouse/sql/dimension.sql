CREATE TABLE IF NOT EXISTS dim_data (
    date_key INT PRIMARY KEY,
    full_date Date NOT NULL,
    day INT,
    month INT,
    year INT,
    day_name varchar(20) 
)

CREATE TABLE IF NOT EXISTS dim_region (
    region_key INTEGER PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_client (
    client_key INTEGER PRIMARY KEY,
    client_name VARCHAR(255),
    client_type VARCHAR(100),
    segment VARCHAR(100),
    region_key INTEGER,
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);

CREATE TABLE IF NOT EXISTS dim_contract_plan (
    contract_plan_key INTEGER PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL UNIQUE,
    monthly_xaf NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS dim_installation (
    installation_key INTEGER PRIMARY KEY,
    installation_id INTEGER NOT NULL UNIQUE,
    client_key INTEGER,
    region_key INTEGER,
    city VARCHAR(100),
    status VARCHAR(50),
    install_date DATE,
    contract_plan_key INTEGER,
    FOREIGN KEY (client_key) REFERENCES dim_client(client_key),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);


CREATE TABLE IF NOT EXISTS dim_distributor (
    distributor_key INTEGER PRIMARY KEY,
    distributor_id VARCHAR(50) NOT NULL UNIQUE,
    distributor_name VARCHAR(255),
    region_key INTEGER,
    since_date DATE,
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);

CREATE TABLE IF NOT EXISTS dim_technician (
    technician_key INTEGER PRIMARY KEY,
    technician_id VARCHAR(50) NOT NULL UNIQUE,
    technician_name VARCHAR(255),
    region_key INTEGER,
    phone VARCHAR(50),
    certified BOOLEAN,
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);

CREATE TABLE IF NOT EXISTS dim_alert (
    alert_key INTEGER PRIMARY KEY,
    alert_code VARCHAR(50) NOT NULL UNIQUE,
    alert_category VARCHAR(100),
    severity VARCHAR(50)
);