import os
from urllib.parse import quote_plus

import boto3
import pandas as pd
from sqlalchemy import create_engine, text


def get_latest_object_key(bucket_name: str, prefix: str = "input/") -> str:
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    contents = resp.get("Contents", [])
    if not contents:
        raise RuntimeError(f"No objects found in s3://{bucket_name}/{prefix}")
    # pick most recently modified
    latest = max(contents, key=lambda o: o["LastModified"])
    return latest["Key"]


def main():
    bucket_name = os.environ["RAW_BUCKET_NAME"]

    pg_user = os.environ["POSTGRES_USER"]
    pg_password = os.environ["POSTGRES_PASSWORD"]
    pg_db = os.environ["POSTGRES_DB"]
    pg_host = os.environ.get("POSTGRES_HOST", "db")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")

    # 1. Find latest CSV in S3 under input/
    key = get_latest_object_key(bucket_name, prefix="input/")
    print(f"Reading from s3://{bucket_name}/{key}")

    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    df = pd.read_csv(obj["Body"])

    # 2. (Optional) further transforms, e.g. filter, sort, etc.
    df = df.sort_values("date")

    # 3. Load into Postgres using SQLAlchemy
    enc_pass = quote_plus(pg_password)
    conn_str = f"postgresql://{pg_user}:{enc_pass}@{pg_host}:{pg_port}/{pg_db}"
    engine = create_engine(conn_str)

     # 4. Upsert into fact_payments using a staging table
    tmp_table = "fact_payments_staging"

    with engine.begin() as conn:
        # Write dataframe to staging (replace each run)
        df.to_sql(tmp_table, conn, if_exists="replace", index=False)

        upsert_sql = text(
            """
            INSERT INTO fact_payments (id, date, amount, load_timestamp)
            SELECT 
                id::integer,
                date::date,
                amount::numeric(12,2),
                load_timestamp::timestamptz
            FROM fact_payments_staging
            ON CONFLICT (id) DO UPDATE
            SET
                date = EXCLUDED.date,
                amount = EXCLUDED.amount,
                load_timestamp = EXCLUDED.load_timestamp;
            """
)
        conn.execute(upsert_sql)

    print(f"Upserted {len(df)} rows into fact_payments")


if __name__ == "__main__":
    main()

