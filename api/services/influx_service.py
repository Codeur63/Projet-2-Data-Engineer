from typing import Dict, Any
from influxdb_client import InfluxDBClient, Point, WritePrecision
from api.core.config import settings


class InfluxService:
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
        )
        self.write_api = self.client.write_api()

    def write_telemetry(self, payload: Dict[str, Any]) -> None:
        point = (
            Point("sensor_telemetry")
            .tag("sensor_id", payload["sensor_id"])
            .tag("installation_id", str(payload["installation_id"]))
            .tag("region", payload["region"])
            .field("solar_output_w", float(payload["solar_output_w"]))
            .field("battery_level_pct", float(payload["battery_level_pct"]))
            .field("consumption_w", float(payload["consumption_w"]))
            .time(payload["timestamp"], WritePrecision.NS)
        )

        if payload.get("alert_code") is not None:
            point = point.tag("alert_code", payload["alert_code"])

        self.write_api.write(
            bucket=settings.influxdb_bucket,
            org=settings.influxdb_org,
            record=point,
        )


influx_service = InfluxService()