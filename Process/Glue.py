import pandas as pd
import os
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import time


class Glue:
    def __init__(self):
        self.glue_client = boto3.client('glue')

    def run_crawler(self, crawler_name): 
        try:
            self.glue_client.start_crawler(crawler_name)
        except Exception as e:
            print("Exception while running the Crwaler")
            print(e)
            return False
        return True


    def run_job(self, job_name):
        myNewJobRun = self.glue_client.start_job_run(JobName=job_name)
        return myNewJobRun

    def get_crawler_status(self, crawler_name):
        count=0
        tries = 100
        response = False
        while count<tries:
            time.sleep(30)
            crawler = self.glue_client.get_crawler(crawler_name)
            crawler_status = crawler['LastCrawl']['Status']
            print(crawler_status)
            if "SUCCEEDED" == crawler_status:
                response = True
                break

            elif "FAILED" == crawler_status or "CANCELLED" ==crawler_status:
                break

            
        return response

    def get_job_status(self, job_name, job_run):
        counter = 0
        max_tries = 100
        response = False
        while counter < max_tries:
            time.sleep(30)
            status = self.glue_client.get_job_run(JobName=job_name, RunId=job_run['JobRunId'])
            print(status['JobRun']['JobRunState'])

            if "SUCCEEDED" == status['JobRun']['JobRunState']:
                response = True
                break
            elif "FAILED" == status['JobRun']['JobRunState'] or "CANCELLED" ==status['JobRun']['JobRunState']:
                break
        return response
