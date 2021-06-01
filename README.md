# PedestrianCountAnalysis
The application calculates -  
1. Top 10 (most pedestrians) locations by day
2. Top 10 (most pedestrians) locations by month

The source data is located in the data folder.

# Appoach 
The application performs an ETL operation as explained below - \
Step 1 - It takes the data from S3 bucket named - step-count-data-bucket-sh\
Step 2 - It creates a data catalog by running a crawler - stepper-crawler-sh\
Step 3 - It triggers an AWS glue Etl job with job name - count-steps-job-sh\
Step 4 - It puts the transformed data in a csv format to another S3 bucket - step-count-output-bucket-sh\
Step 5 - It puts the transformed data in postgres databases - rds-sh with datbase name MyDB

# Architecture
![](img/Architecture.png)

# Pre-Requisites
```sh
- AWS Credentials
- Terraform
- python3.x
```

# Data Files - 
## !! This is important !!
Download the Count file from  -  
[Pedestrian-Counting-System-Monthly-Counts](https://data.melbourne.vic.gov.au/Transport/Pedestrian-Counting-System-Monthly-counts-per-hour/b2ak-trbp)

Download the Sensor Data from  -   
[Pedestrian-Counting-System-Sensor](https://data.melbourne.vic.gov.au/Transport/Pedestrian-Counting-System-Sensor-Locations/h57g-5234)

Replace the files the data folder of the project.

# Setup - 
1. configure aws credentials - 
```aws
 aws configure  
```
    AWS Access Key ID [None]: your access key id XXXXX  
    AWS Secret Access Key [None]: your secret access key  XXXXX  
    Default region name [None]: ap-southeast-2  
    Default output format [None]: json  

2. Install terraform  - 
    [How to install terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

3. Create virtual environment in the project root folder(optional)
    $ python3 -m venv .venv

# Run - 
1. Initiate terraform in the project root folder - 
    $ terraform init

2. Deploy the infra to aws  - 
    $ terraform apply

3. Activate virtual environment -
    $ source .venv/bin/activate

4. Install dependancies - 
    $ pip install -r requirements.txt

5.  Run the main.py script
    $ python main.py 

# Output
