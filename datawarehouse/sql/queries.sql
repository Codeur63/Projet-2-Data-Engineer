
-- 1. CA total par région
SELECT
    r.region_name,
    SUM(p.amount_xaf) AS total_revenue_xaf
FROM fact_payments p
JOIN dim_installation i ON p.installation_key = i.installation_key
JOIN dim_region r ON i.region_key = r.region_key
WHERE p.payment_status = 'paid'
GROUP BY r.region_name
ORDER BY total_revenue_xaf DESC;

-- 2. Production solaire moyenne par jour
SELECT
    d.full_date,
    AVG(t.avg_solar_output_w) AS avg_solar_output_w,
    AVG(t.avg_battery_level_pct) AS avg_battery_pct,
    SUM(t.alert_count) AS total_alerts
FROM fact_telemetry_daily t
JOIN dim_date d ON t.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;

-- 3. Alertes par type
SELECT
    a.alert_code,
    a.severity,
    SUM(t.alert_count) AS total_alerts
FROM fact_telemetry_daily t
JOIN dim_alert a ON t.alert_key = a.alert_key
GROUP BY a.alert_code, a.severity
ORDER BY total_alerts DESC;

-- 4. Top distributeurs par installations vendues
SELECT
    dist.distributor_id,
    dist.distributor_name,
    COUNT(DISTINCT f.installation_key) AS installations_sold
FROM fact_sales_network f
JOIN dim_distributor dist ON f.distributor_key = dist.distributor_key
WHERE f.relation_type = 'SOLD'
GROUP BY dist.distributor_id, dist.distributor_name
ORDER BY installations_sold DESC
LIMIT 10;

-- 5. Maintenance corrective par région
SELECT
    r.region_name,
    COUNT(*) AS corrective_interventions,
    SUM(m.cost_xaf) AS total_cost_xaf
FROM fact_maintenance m
JOIN dim_installation i ON m.installation_key = i.installation_key
JOIN dim_region r ON i.region_key = r.region_key
WHERE m.corrective_flag = TRUE
GROUP BY r.region_name
ORDER BY corrective_interventions DESC;

-- 6. Installations les plus coûteuses en maintenance
SELECT
    i.installation_id,
    r.region_name,
    COUNT(*) AS interventions,
    SUM(m.cost_xaf) AS total_maintenance_cost_xaf
FROM fact_maintenance m
JOIN dim_installation i ON m.installation_key = i.installation_key
JOIN dim_region r ON i.region_key = r.region_key
GROUP BY i.installation_id, r.region_name
ORDER BY total_maintenance_cost_xaf DESC
LIMIT 10;