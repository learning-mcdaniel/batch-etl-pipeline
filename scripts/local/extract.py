"""
Script Name:  extract.py
Author:       Kevin McDaniel
Date:         2026-0608
Description:  This script extracts data from the Bank_Churn SQLite database into
the bank_churn_raw.csv file, which is located in S3://kevin-data-engineering-lab-2026/raw.

"""

import os
import boto3
import logging
import sqlite3
import pandas as pd
from datetime import datetime
from io import StringIO

#------------------------------------------------------
# Configuration
#------------------------------------------------------

s3 = boto3.client("s3")

BUCKET = "kevin-data-engineering-lab-2026"

db_path = r"F:\Learning\Projects\batch-etl-pipeline\db\bank_churn.db"

RAW_KEY = "raw/bank_churn_raw.csv"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_FILE = rf"F:\Learning\Projects\batch-etl-pipeline\logs\extract_{TIMESTAMP}.log"
LOG_KEY = f"logs/extract_{TIMESTAMP}.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(LOG_FILE,mode="w",encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

#------------------------------------------------------
# Extraction Process
#------------------------------------------------------

def extract_data(

    query = """SELECT
                    ai.CustomerId,
                    ci.Surname,
                    ci.Geography,
                    ci.Gender,
                    ci.Age,
                    ci.Tenure,
                    ai.Balance,
                    ai.NumOfProducts,
                    ai.HasCrCard,
                    ai.IsActiveMember,
                    ci.EstimatedSalary,
                    ai.Exited
                FROM  Account_Info ai, Customer_info ci
                WHERE
                    ai.CustomerId = ci.CustomerId
                """
                ):
    # Verify that the database file actually exists first
    print("Current working directory:", os.getcwd())
    print("Checking:", db_path)
    print("Exists:", os.path.exists(db_path))
    if not os.path.exists(db_path):
        print(f"Error: The database file '{db_path}' could not be found.")
        return False

    conn = None
    try:
        # 1. Connect to the SQLite database

        conn = sqlite3.connect(db_path)

        # 2. Load the data into a Pandas DataFrame
        df = pd.read_sql_query(query, conn)


        # 3. Export the extracted data to a CSV file

        s3.put_object(
            Bucket = BUCKET,
            Key = RAW_KEY,
            Body = df.to_csv(index=False)
            )

        logger.info(f"Successfully extracted data to s3://{BUCKET}/{RAW_KEY}")
#        print(f"Successfully extracted data to S3://{BUCKET}/{RAW_KEY}")
        logger.info(f"Total records exported: {len(df)}")
#        print(f"Total records exported: {len(df)}")
        return True

    except sqlite3.Error as db_error:
        logger.info(f"Database error: {db_error}")
#        print(f"Database error: {db_error}")
        return False

    except Exception as general_error:
        logger.info(f"An unexpected error occurred during extraction: {general_error}")
#        print(f"An unexpected error occurred during extraction: {general_error}")
        return False

    finally:
        # 5. Always close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    success = extract_data()

    for handler in logger.handlers:
        handler.flush()
        handler.close()

    if success:
        logger.info("Extraction job completed.")
    else:
        logger.info("Extraction job failed.")

    s3.upload_file(
         Filename=LOG_FILE,
	 Bucket=BUCKET,
	 Key=LOG_KEY
    )


