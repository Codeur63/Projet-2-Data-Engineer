from solarmboa_influxdb.writer import write_telemetry

if __name__ == "__main__":
    write_telemetry(
        sensor_id="CAM-0001-S1",
        region="Littoral",
        solar_output_w=650.0,
        battery_pct=72.0,
        consumption_w=250.0,
        alert_code=None,
    )

    print("Mesure IoT envoyée dans InfluxDB.")