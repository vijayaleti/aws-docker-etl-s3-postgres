import os
import uuid
from datetime import datetime

import boto3
import pandas as pd


def main():
    bucket_name = os.environ["RAW_BUCKET_NAME"]
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    # 1. Read local CSV with pandas
    input_path = "data/input.csv"
    df = pd.read_csv(input_path)

    # 2. Tiny transform: ensure date is parsed and add a load_timestamp column
    df["date"] = pd.to_datetime(df["date"])
    df["load_timestamp"] = datetime.utcnow().isoformat()

    # 3. Save to a temporary file before upload
    output_key = f"input/processed_{uuid.uuid4().hex}.csv"
    tmp_path = "/tmp/processed.csv"
    df.to_csv(tmp_path, index=False)

    # 4. Upload to S3 using boto3 (picks up AWS_* env vars)
    s3 = boto3.client("s3", region_name=region)
    s3.upload_file(tmp_path, bucket_name, output_key)

    print(f"Uploaded {tmp_path} to s3://{bucket_name}/{output_key}")


if __name__ == "__main__":
    main()
