"""
Script Name:  transform.py
Author:       Kevin McDaniel
Date:         2026-0608
Description:  This script handles data transformation of the bank_churn_raw.csv file
and places a cleaned version (bank_churn_cleaned) into the processed directory.

"""
import os
import boto3
import logging
import pandas as pd
from pandas.errors import EmptyDataError
from datetime import datetime
from io import StringIO

#-------------------------------------------
# Configuration
#-------------------------------------------

s3 = boto3.client("s3")

BUCKET = "kevin-data-engineering-lab-2026"

RAW_KEY = "raw/bank_churn_raw.csv"
#RAW_FILE = r"F:\Learning\Projects\batch-etl-pipeline\data\raw\bank_churn_raw.csv"

CLEAN_KEY = "processed/bank_churn_clean.csv"
#CLEAN_FILE = r"F:\Learning\Projects\batch-etl-pipeline\data\processed\bank_churn_clean.csv"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

#LOG_FILE = rf"\Projects\batch-etl-pipeline\logs\transform_{TIMESTAMP}.log"
LOG_DIR = "/home/ec2-user/projects/batch-etl-pipeline/logs"
os.makedirs(LOG_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"{LOG_DIR}/transform_{TIMESTAMP}.log"
LOG_KEY = f"logs/transform_{TIMESTAMP}.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(LOG_FILE,mode="w",encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

#-------------------------------------------
# Transformation Process
#-------------------------------------------

def transform_data():
    try:
        logger.info("Starting transformation job.")
        logger.info(f"Reading source file from S3: {RAW_KEY}")

        obj = s3.get_object(
            Bucket = BUCKET,
            Key = RAW_KEY
            )

#       df = pd.read_csv(RAW_FILE)
        df = pd.read_csv(obj["Body"])
        #-------------------------------------------
        # Remove currency symbol from salary field
        #-------------------------------------------

        df["EstimatedSalary"] = (
            df["EstimatedSalary"]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        df["EstimatedSalary"] = pd.to_numeric(
            df["EstimatedSalary"],
            errors="coerce"
        )

        #-------------------------------------------
        # Remove currency symbol from balance field
        #-------------------------------------------

        df["Balance"] = (
            df["Balance"]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        df["Balance"] = pd.to_numeric(
            df["Balance"],
            errors="coerce"
        )

        #-------------------------------------------
        # Remove duplicate rows
        #-------------------------------------------

        original_count = len(df)

        logger.info(f"Beginning row count: {original_count}")

        df_cleaned = df.drop_duplicates()

        cleaned_count = len(df_cleaned)
        duplicates_removed = original_count - cleaned_count

        logger.info(f"Removed {duplicates_removed} duplicate rows.")
        logger.info(f"Cleaned record count: {cleaned_count}")

#       df_cleaned.to_csv(CLEAN_FILE, index=False)

        buffer = StringIO()

        df_cleaned.to_csv(
            buffer,
            index=False
        )

        s3.put_object(
            Bucket=BUCKET,
            Key=CLEAN_KEY,
            Body=buffer.getvalue()
        )

        logger.info(f"Writing cleaned file to S3: {CLEAN_KEY}")
        logger.info("Transformation completed successfully.")

        return True

    except EmptyDataError:
        logger.error("Source CSV file is empty")
        return False

    except FileNotFoundError as file_error:
        logger.error(f"File not found: {file_error}")
        return False

    except Exception as error:
        logger.exception(f"Unexpected error: {error}")
        return False

if __name__ == "__main__":

    success = transform_data()

    try:


        s3.upload_file(
            Filename=LOG_FILE,
            Bucket=BUCKET,
            Key=LOG_KEY
        )

        print(f"Log uploaded to s3://{BUCKET}/{LOG_KEY}")

    except Exception as e:
        print(f"Failed to upload log file: {e}")

    if success:
        logger.info("Transformation job completed.")
    else:
        logger.info("Transformation job failed.")

    for handler in logger.handlers:
        handler.flush()
        handler.close()

