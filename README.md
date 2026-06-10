
## Overview

This is an ETL pipeline project that simulates a real-world batch ETL pipeline workflow, including upstream issues, error-handling and logging.  This project demonstrates core data engineering 
concepts, including:

- Relational databases & SQL proficiency
- Batch data extraction, transformation & loading
- Cloud resource utilization
- Python coding skills and knowledge as it applies to ETL pipelines
- Proper logging and error handling
- Understanding of the batch ETL pipeline process
- Modular pipeline workflow

---

## Features

  - Extract data from a database into a local batch file and store it in S3
  - Transform the data and save it to a new file in the clean directory in S3
  - Load the data into the Amazon DW
  - Save any failed records into an exceptions CSV file for review


---

## Technology Stack

| Component       | Technology         |
| --------------- | ------------------ |
| Language        | Python 3           |
| Data Processing | Pandas             |
| Cloud Provider  | Amazon AWS         |
| Database        | SQLite, PostgreSQL |
| Version Control | Git                |
| Storage         | S3                 |
| Compute         | EC2                |

---

## Project Structure

└── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)data  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)archive  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)clean  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)errors  
        ├── exceptions_20260610_162656.csv  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)processed  
        ├── bank_churn_clean.csv  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)raw  
        ├── bank_churn_raw.csv  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)source  
        └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)Bank+Customer+Churn  
            ├── Bank_Churn_Data_Dictionary.csv  
            ├── Bank_Churn_Messy.xlsx  
            ├── Bank_Churn.csv  
        └── Bank+Customer+Churn.zip  
└── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)db  
    ├── bank_churn.db  
...
└── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)logs  
    └── extract_20260610_121826.log  
└── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)scripts  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)aws  
        ├── load.py  
        ├── transform.py  
    └── ![:file_folder:](https://a.slack-edge.com/production-standard-emoji-assets/16.0/google-medium/1f4c1.png)local  
        ├── extract.py


---

## Pipeline Workflow
![Workflow Diagram](workflow-diagram.png)
![[workflow-diagram.png]]


---


## Getting Started

#### Pre-requisites:
- [ ] Local SQLite database with bank_churn table. (SQL and CSV files provided under /source)
- [ ] AWS S3 bucket with these folders:
    *errors/
    processed/
    raw/*
- [ ] AWS RDS database with a dw_bank table. (SQL provided under /source)
- [ ] EC2 instance with:
	*Security Group with local and RDS access
	following folders:*
		- /home/ec2-user/batch-etl-pipeline/scripts
		- /home/ec2-user/batch-etl-pipeline/logs
- [ ] AWS IAM User Group with AdminAccessAll assigned to AWS user


#### Steps

| Actions                                                                                                                                                                      | Screenshot                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Step 1.  Locally, run the ./scripts/extract.py script<br>*This will produce the bank_churn_raw.csv file and store it in the S3://{YOUR_BUCKET}/raw folder.*                  | ![[extract_screenshot.png]]   ![[raw_csv_screenshot.png]]  |
| Step 2.  In EC2 instance, run the ./scripts/transform.py script<br>*This will create the bank_churn_clean.csv file and store it in the S3://{YOUR_BUCKET}/processed folder.* | ![[transform_screenshot.png]]![[clean_csv_screenshot.png]] |
| Step 3.  In EC instance, run the ./scripts/load.py script<br>*This will load the "cleaned" data into the dw_bank database.*                                                  | ![[load_screenshot.png]]![[bank_dw_data_screenshot.png]]   |
| *Any records that failed to load will be found in an exception_{TIMESTAMP}.csv file located in the S3://{YOUR_BUCKET}/errors folder for review.*                             | ![[exceptions_csv_screenshot.png]]                         |




---

## Challenges Encountered  
  
During development I encountered several real-world cloud engineering challenges:  
  
- AWS IAM configuration  
- EC2 environment setup  
- S3 file transfers  
- PostgreSQL RDS deployment  
- EC2 to RDS network connectivity  
- Security group configuration  
- Python dependency management  
  
Resolving these issues provided hands-on experience with AWS infrastructure and cloud troubleshooting.


---

## Learning Objectives
This project demonstrates practical experience with:

- Python programming
- Batch ETL processing
- Database design
- AWS S3 and EC2 concepts
- Version control with Git


## License
This project is provided for educational and portfolio purposes.
