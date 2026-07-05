CREATE TABLE IF NOT EXISTS fact_telemetry_daily (
    telemetry_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL,
    installation_key INTEGER NOT NULL,
    alert_key INTEGER,

    avg_solar_output_w NUMERIC(12, 2),
    max_solar_output_w NUMERIC(12, 2),
    avg_battery_level_pct NUMERIC(5, 2),
    min_battery_level_pct NUMERIC(5, 2),
    avg_consumption_w NUMERIC(12, 2),
    alert_count INTEGER,

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (installation_key) REFERENCES dim_installation(installation_key),
    FOREIGN KEY (alert_key) REFERENCES dim_alert(alert_key)
);

CREATE TABLE IF NOT EXISTS fact_payments (
    payment_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL,
    installation_key INTEGER NOT NULL,

    payment_id VARCHAR(100),
    amount_xaf NUMERIC(12, 2),
    payment_status VARCHAR(50),
    payment_method VARCHAR(50),

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (installation_key) REFERENCES dim_installation(installation_key)
);

CREATE TABLE IF NOT EXISTS fact_maintenance (
    maintenance_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL,
    installation_key INTEGER NOT NULL,
    technician_key INTEGER,

    maintenance_type VARCHAR(100),
    duration_minutes INTEGER,
    cost_xaf NUMERIC(12, 2),
    corrective_flag BOOLEAN,

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (installation_key) REFERENCES dim_installation(installation_key),
    FOREIGN KEY (technician_key) REFERENCES dim_technician(technician_key)
);

CREATE TABLE IF NOT EXISTS fact_sales_network (
    sales_network_key INTEGER PRIMARY KEY,
    date_key INTEGER,
    installation_key INTEGER NOT NULL,
    distributor_key INTEGER,
    technician_key INTEGER,

    relation_type VARCHAR(50),
    relation_weight NUMERIC(10, 2),

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (installation_key) REFERENCES dim_installation(installation_key),
    FOREIGN KEY (distributor_key) REFERENCES dim_distributor(distributor_key),
    FOREIGN KEY (technician_key) REFERENCES dim_technician(technician_key)
);