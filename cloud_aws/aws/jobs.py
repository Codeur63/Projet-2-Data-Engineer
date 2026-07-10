import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType


args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "BUCKET",
    ],
)

BUCKET = args["BUCKET"]

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# ============================================================
# Paths
# ============================================================

BRONZE = f"s3://{BUCKET}/bronze"
SILVER = f"s3://{BUCKET}/silver"


telemetry_raw_path = f"{BRONZE}/iot/sensors_telemetry.csv"
telemetry_silver_path = f"{SILVER}/iot_clean/"

telemetry = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(telemetry_raw_path)
)

telemetry_clean = (
    telemetry
    .withColumn("installation_id", F.col("installation_id").cast(IntegerType()))
    .withColumn("solar_output_w", F.col("solar_output_w").cast(DoubleType()))
    .withColumn("battery_level_pct", F.col("battery_level_pct").cast(DoubleType()))
    .withColumn("consumption_w", F.col("consumption_w").cast(DoubleType()))
    .withColumn("timestamp", F.to_timestamp("timestamp"))
    .withColumn("region", F.trim(F.col("region")))
    .withColumn("alert_code", F.trim(F.col("alert_code")))
    .dropna(subset=["sensor_id", "installation_id", "timestamp"])
    .dropDuplicates(["sensor_id", "installation_id", "timestamp"])
)

telemetry_clean = telemetry_clean.filter(
    (F.col("solar_output_w") >= 0)
    & (F.col("battery_level_pct") >= 0)
    & (F.col("battery_level_pct") <= 100)
    & (F.col("consumption_w") >= 0)
)

(
    telemetry_clean
    .write
    .mode("overwrite")
    .parquet(telemetry_silver_path)
)


installations_raw_path = f"{BRONZE}/installations/installations.json"
installations_silver_path = f"{SILVER}/installations_clean/"

installations = spark.read.json(installations_raw_path)

installations_clean = (
    installations
    .withColumn("installation_id", F.col("installation_id").cast(IntegerType()))
    .withColumn("region", F.trim(F.col("region")))
    .withColumn("city", F.trim(F.col("city")))
    .withColumn("status", F.lower(F.trim(F.col("status"))))
    .withColumn("tariff_plan", F.trim(F.col("tariff_plan")))
    .withColumn("install_date", F.to_date("install_date"))
    .dropna(subset=["installation_id"])
    .dropDuplicates(["installation_id"])
)

(
    installations_clean
    .write
    .mode("overwrite")
    .parquet(installations_silver_path)
)


payments_raw_path = f"{BRONZE}/payments/payments.csv"
payments_silver_path = f"{SILVER}/payments_clean/"

payments = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(payments_raw_path)
)

payments_clean = (
    payments
    .withColumn("installation_id", F.col("installation_id").cast(IntegerType()))
    .withColumn("amount_xaf", F.col("amount_xaf").cast(DoubleType()))
    .withColumn("payment_date", F.to_timestamp("payment_date"))
    .withColumn("status", F.lower(F.trim(F.col("status"))))
    .withColumn("channel", F.lower(F.trim(F.col("channel"))))
    .dropna(subset=["payment_id", "installation_id", "payment_date"])
    .dropDuplicates(["payment_id"])
)

payments_clean = payments_clean.filter(F.col("amount_xaf") >= 0)

(
    payments_clean
    .write
    .mode("overwrite")
    .parquet(payments_silver_path)
)


network_files = {
    "network_graph": "network_graph.csv",
    "network_nodes_distributors": "network_nodes_distributors.csv",
    "network_nodes_technicians": "network_nodes_technicians.csv",
}

for table_name, file_name in network_files.items():
    input_path = f"{BRONZE}/networks/{file_name}"
    output_path = f"{SILVER}/networks_clean/{table_name}/"

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(input_path)
    )

    clean_df = df.dropDuplicates()

    (
        clean_df
        .write
        .mode("overwrite")
        .parquet(output_path)
    )


job.commit()