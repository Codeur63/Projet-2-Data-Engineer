from datetime import datetime, timezone
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from .client import get_influx_client
from .config import settings


def write_telemetry(
    sensor_id: str,
    region: str,
    solar_output_w: float,
    battery_level_pct: float,
    consumption_w: float,
    alert_code: str | None = None,
    timestamp: datetime | None = None,
) -> None:
    ts = timestamp or datetime.now(timezone.utc)

    point = (
        Point("sensor_telemetry")
        .tag("sensor_id", sensor_id)
        .tag("region", region)
        .field("solar_output_w", float(solar_output_w))
        .field("battery_level_pct", float(battery_level_pct))
        .field("consumption_w", float(consumption_w))
        .time(ts, WritePrecision.NS)
    )

    if alert_code:
        point = point.tag("alert_code", alert_code)

    client = get_influx_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    write_api.write(
        bucket=settings.influxdb_bucket,
        org=settings.influxdb_org,
        record=point,
    )