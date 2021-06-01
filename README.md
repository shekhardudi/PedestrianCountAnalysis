# PedestrianCountAnalysis
The application calculates top ten monthy and daily pedestrians by location.
The source data is located in the data folder.

# Appoach 
The application performs an ETL operation as explained below - 
Step 1 - It takes the data from S3 bucket named - step-count-data-bucket-sh
Step 2 - It creates a data catalog by running a crawler - stepper-crawler-sh
Step 3 - It triggers an AWS glue Etl job with job name - count-steps-job-sh
Step 4 - It puts the transformed data in a csv format to another S3 bucket - step-count-output-bucket-sh
Step 5 - It puts the transformed data in postgres databases - rds-sh with datbase name MyDB

# Architecture
![](img/Architecture.png)

# Pre-Requisites
AWS creadentials file