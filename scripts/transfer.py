import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def upload_to_s3(
    local_file=r"F:\Learning\Projects\batch-etl-pipeline\data\raw\bank_churn_raw.csv",
    bucket_name="kevin-data-engineering-lab-2026",
    s3_key="raw/bank_churn_raw.csv"
    ):
    """
    Upload a local CSV file to an S3 bucket.
    """

    # Verify local file exists
    if not os.path.exists(local_file):
        print(f"Error: File not found: {local_file}")
        return False

    try:
        s3_client = boto3.client("s3")

        s3_client.upload_file(
            Filename=local_file,
            Bucket=bucket_name,
            Key=s3_key
        )

        print(
            f"Successfully uploaded '{local_file}' "
            f"to 's3://{bucket_name}/{s3_key}'"
        )
        return True

    except NoCredentialsError:
        print("AWS credentials not found.")
        return False

    except ClientError as e:
        print(f"AWS error: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    upload_to_s3()
