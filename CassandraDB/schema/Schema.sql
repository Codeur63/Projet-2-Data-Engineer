
-- Lire les données par jours 
create table sensor_readings_by_day (
    sensor_id text,
    bucket date,
    timestamp timestamp,
    installation_id int,
    region text,
    solar_output_w float,
    battery_level_pct float,
    consumption_w float,
    alert_code text,
    
    primary key ((sensor_id, bucket), timestamp)
) with clustering order by (timestamp desc)


-- Lire les données par région
create table sensor_readings_by_region(
    sensor_id text, 
    bucket date, 
    timestamp timestamp,
    installation_id int,
    region text,
    solar_output_w float,
    battery_level_pct float,
    consumption_w float,
    alert_code text,

    primary key((region, bucket), timestamp, sensor_id)
) with clustering order by (
    timestamp desc, 
    sensor_id asc
)

-- Lire les données
create table sensor_readings (
    sensor_id text,
    bucket date, 
    timestamp timestamp,
    region text, 
    solar_output_w float,
    battery_level_pct float,
    consumption_w float,
    alert_code text,
    signal_rssi int,
    temp_c float,
    primary key ((sensor_id, bucket), timestamp)
) with clustering order by (timestamp desc)
and default_time_to_live = 94608000
and compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
} ;


-- Alerts par région et date
create table sensor_alerts (
    sensor_id text,
    bucket date,
    timestamp timestamp,
    region text,
    solar_output_w float,
    alert_type text, -- Battery_LOW, OVERVOLTAGE, NO_SIGNAL
    severity text, -- WARNING, CRITICAL
    value float,
    acknowledged boolean, 
    primary key ((region, bucket), timestamp, sensor_id)
) with clustering order by (timestamp desc, sensor_id asc)
and default_time_to_live = 7776000;


-- Derniere mesure
create table sensor_last_reading(
    sensor_id text primary key,
    timestamp timestamp,    
    installation_id int,
    region text,
    solar_output_w float,
    battery_level_pct float,
    consumption_w float,
    alert_code text,
    status text, -- 'Ok', 'Warning', 'Critical', 'OFFLINE'
);

-- Statistiques journalières par installation
create table daily_stats (
    installation_id int, 
    stat_date date,
    sensor_id text,
    avg_solar_w float,
    max_solar_w float,
    min_battery_pct float,
    total_kwh float,
    uptime_pct float, --- % du temps où le panneau produisait
    nb_alerts int,
    primary key ((installation_id, stat_date), sensor_id)  
);