import pandas as pd
import os
import logging
import boto3
from botocore.exceptions import ClientError
import config
from botocore.exceptions import NoCredentialsError
import time

def upload(file_path, bucket):
    file_dir, file_name = os.path.split(file_path)
    try:
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f,bucket,file_name)
    except Exception as e:
        print("Exception in uploading the file to S3")
        print(e)
        return False
    return True

def run_crawler(): 
    try:
        glue_client.start_crawler(Name=config.crawler_name)
    except Exception as e:
        print("Exception while running the Crwaler")
        print(e)
        return False
    return True


def run_job():
    myNewJobRun = glue_client.start_job_run(JobName=config.glue_job_name)
    return myNewJobRun

def get_crawler_status():
    count=0
    tries = 100
    response = False
    while count<tries:
        time.sleep(30)
        crawler = glue_client.get_crawler(config.crawler_name)
        crawler_status = crawler['LastCrawl']['Status']
        print(crawler_status)
        if "SUCCEEDED" == crawler_status:
            response = True
            break

        elif "FAILED" == crawler_status or "CANCELLED" ==crawler_status:
            break

        
    return response

def get_job_status(job_run):
    counter = 0
    max_tries = 100
    response = False
    while counter < max_tries:
        time.sleep(30)
        status = glue_client.get_job_run(JobName=config.glue_job_name, RunId=job_run['JobRunId'])
        print(status['JobRun']['JobRunState'])

        if "SUCCEEDED" == status['JobRun']['JobRunState']:
            response = True
            break
        elif "FAILED" == status['JobRun']['JobRunState'] or "CANCELLED" ==status['JobRun']['JobRunState']:
            break

        
    return response


if __name__ == '__main__':
    try:
        # Create clients
        s3 = boto3.client('s3')
        glue_client = boto3.client('glue')
        print("Process Started")
        #Upload Csv Data
        res = upload(file_path=os.path.join('data','Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv'),
                    bucket=config.source_data_bucket)
        if res:
            print('Pedestrian Count Csv upload successful')

            res = upload(file_path=os.path.join('data','Pedestrian_Counting_System_-_Sensor_Locations.csv'),
                    bucket=config.source_data_bucket)
            if res:
                print('Sensor data uploaded successfully')
            else:
                print('Sensor upload failed. Can not continue')
                exit(1)
        else:
            print('Pedestrian count upload failed. Can not continue')
            exit(1)

        res = upload(file_path='GlueJob.py',
                    bucket=config.script_bucket)
        if res:
            print('Glue Script uploaded successfully')
        else:
            print('Glue Script upload failed. Can not continue')
            exit(1)
        
        run_crawler()
        status = get_crawler_status()

        if status:
            print('Crawler Run Complete')
        else:
            print('Could not catalog data')
            exit(1)
        
        job_run = run_job()
        resp = get_job_status(job_run=job_run)
        if resp:
            print("Glue Job finished Successfully!")
        else:
            print("Glue Job Failed")
        

    except Exception as e:
        print(e)

