"""
Script Name:  load.py
Author:       Kevin McDaniel
Date:         2026-0608
Description:  This script loads the bank_churn_clean.csv file into the AWS Bank DW.
If any records fail to load, they are written to an exceptions CSV file for review.

"""

import logging
import time
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd
import psycopg2
from botocore.exceptions import ClientError, NoCredentialsError

# ==========================================================

# CONFIGURATION

# ==========================================================

BUCKET_NAME = "kevin-data-engineering-lab-2026"

INPUT_KEY = "processed/bank_churn_clean.csv"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

ERROR_KEY = f"errors/exceptions_{TIMESTAMP}.csv"
LOG_KEY = f"logs/load_{TIMESTAMP}.log"

LOCAL_LOG_FILE = f"/home/ec2-user/projects/batch-etl-pipeline/logs/load_{TIMESTAMP}.log"


DB_HOST = "postgres-etl-lab.c3k0ikys8001.us-east-2.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "bank_dw"
DB_USER = "postgres"
DB_PASSWORD = "Rocko46350"

# ==========================================================

# LOGGING

# ==========================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# This logs messages to the screen.
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# This logs messages to the logfile
file_handler = logging.FileHandler(
        LOCAL_LOG_FILE,
        mode="w",
        encoding="utf-8"
        )

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ==========================================================

# SQL MAPPING

# We're not batch loading because we want rows that failed to
# load to go to an exceptions file.

# ==========================================================

INSERT_SQL = """
    INSERT INTO DW.bank_churn
    (
    "CustomerId",
    "Surname",
    "Country",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "Products",
    "CreditCard",
    "ActiveMember",
    "EstimatedSalary",
    "Churned"
    )
    VALUES
    (
    %s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s
    )
"""

# Defining the file to be uploaded
def upload_file_to_s3(local_file, s3_key):

    s3_client = boto3.client("s3")

    s3_client.upload_file(
        local_file,
        BUCKET_NAME,
        s3_key
    )

# Creating a DataFrame to load the CSV data
def upload_dataframe_to_s3(df, s3_key):

    csv_buffer = StringIO()

    df.to_csv(
        csv_buffer,
        index=False
    )

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=csv_buffer.getvalue()
    )


def transform_row(row):
    """
    Map source CSV structure to DW structure.
    """

    return (
        row["CustomerId"],
        row["Surname"],
        row["Geography"],
        row["Gender"],
        row["Age"],
        row["Tenure"],
        row["Balance"],
        row["NumOfProducts"],
        row["HasCrCard"],
        row["IsActiveMember"],
        row["EstimatedSalary"],
        row["Exited"]
    )

# Function to test the connectivity to the DW
def test_database_connection():
    """
    Test connectivity to PostgreSQL.
    """
    try:
        logger.info("Testing database connection...")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        logger.info("Database connection successful.")

        conn.close()

        return True

    except Exception as error:
        logger.error(
            f"Database connection failed: {error}"
        )
        return False
# Fuction for loading the CSV data
def load_data():

    start_time = time.time()

    rows_read = 0
    rows_loaded = 0
    rows_rejected = 0
    duplicate_rows = 0

    exception_rows = []

    conn = None

    try:

        logger.info("Starting load process.")

        # --------------------------------------------------
        # Read cleaned file from S3
        # --------------------------------------------------

        s3_client = boto3.client("s3")

        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=INPUT_KEY
        )

        csv_content = (
            response["Body"]
            .read()
            .decode("utf-8")
        )

        df = pd.read_csv(StringIO(csv_content))

        rows_read = len(df)

        logger.info(
            f"Source rows read: {rows_read}"
        )

        # --------------------------------------------------
        # Connect to PostgreSQL
        # --------------------------------------------------

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cursor = conn.cursor()

        # --------------------------------------------------
        # Process in row-by-row
        # --------------------------------------------------

        for _, row in df.iterrows():

            try:

                cursor.execute(
                    INSERT_SQL,
                    transform_row(row)
                )

                conn.commit()

                rows_loaded += 1
#
#            except psycopg2.errors.UniqueViolation:
#
#                conn.rollback()
#
#                duplicate_rows += 1
#                rows_rejected += 1
#
#                rejected_row = row.to_dict()
#                rejected_row["error_message"] = (
#                    "Duplicate CustomerId"
#                )
#
#                exception_rows.append(
#                    rejected_row
#                )
#
#                logger.warning(
#                    f"Duplicate CustomerId: "
#                    f"{row['CustomerId']}"
#                )
#
            except Exception as row_error:

                conn.rollback()

                rows_rejected += 1

                rejected_row = row.to_dict()

                rejected_row["error_message"] = (
                    str(row_error)
                )

                exception_rows.append(
                    rejected_row
                )

                logger.warning(
                    f"Rejected CustomerId "
                    f"{row['CustomerId']}: "
                    f"{row_error}"
                )

        # --------------------------------------------------
        # Save exception file
        # --------------------------------------------------

        if exception_rows:

            exception_df = pd.DataFrame(
                exception_rows
            )

            upload_dataframe_to_s3(
                exception_df,
                ERROR_KEY
            )

            logger.info(
                f"Exception file written: "
                f"s3://{BUCKET_NAME}/{ERROR_KEY}"
            )

        elapsed_time = round(
            time.time() - start_time,
            2
        )

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        logger.info("========== LOAD METRICS ==========")

        logger.info(
            f"Rows Read: {rows_read}"
        )

        logger.info(
            f"Rows Loaded: {rows_loaded}"
        )

        logger.info(
            f"Rows Rejected: {rows_rejected}"
        )

        logger.info(
            f"Duplicate Rows: {duplicate_rows}"
        )

        logger.info(
            f"Execution Time (sec): "
            f"{elapsed_time}"
        )

        logger.info(
            "Load completed successfully."
        )

        return True

    except NoCredentialsError:

        logger.error("AWS credentials not found.")
        return False

    except ClientError as aws_error:

        logger.error(
            f"AWS error: {aws_error}"
        )

        return False

    except Exception as error:

        logger.exception(
            f"Load failed: {error}"
        )

        return False

    finally:

        if conn:
            conn.close()

        for handler in logger.handlers:
            handler.flush()

        try:

            upload_file_to_s3(
                LOCAL_LOG_FILE,
                LOG_KEY
            )

        except Exception as log_error:

            logger.error(
                f"Failed to upload log file: "
                f"{log_error}"
            )

if __name__ == "__main__":

    if test_database_connection():
        load_data()
    else:
        logger.error(
            "Load process aborted due to database connection failure."
        )

