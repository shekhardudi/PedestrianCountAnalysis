import pandas as pd
import os
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import time


class GlueProcessor:
    def __init__(self):
        self.glue_client = boto3.client('glue')

    def run_crawler(self, crawler_name): 
        try:
            self.glue_client.start_crawler(Name=crawler_name)
        except Exception as e:
            print("Exception while running the Crwaler")
            print(e)
            return False
        return True


    def run_job(self, job_name):
        myNewJobRun = self.glue_client.start_job_run(JobName=job_name)
        return myNewJobRun

    def get_crawler_status(self, crawler_name):
        try:
            count=0
            tries = 60
            response = False
            while count<tries:
                time.sleep(30)
                try:
                    crawler = self.glue_client.get_crawler(Name=crawler_name)
                    crawler_status = crawler['Crawler']['LastCrawl']['Status']
                    print('Crawler status - {}'.format(crawler_status))
                    if "SUCCEEDED" == crawler_status:
                        response = True
                        break

                    elif "FAILED" == crawler_status or "CANCELLED" ==crawler_status:
                        break
                except KeyError:
                    print("Waiting for crawler to finish")
        except Exception as e:
            print('Error in getting crawler status')
            print(e)

            
        return response

    def get_job_status(self, job_name, job_run):
        counter = 0
        max_tries = 60
        response = False
        while counter < max_tries:
            time.sleep(30)
            status = self.glue_client.get_job_run(JobName=job_name, RunId=job_run['JobRunId'])
            current_status = status['JobRun']['JobRunState']
            print('glue job status - {}'.format(current_status))

            if "SUCCEEDED" == status['JobRun']['JobRunState']:
                response = True
                break
            elif "FAILED" == status['JobRun']['JobRunState'] or "CANCELLED" ==status['JobRun']['JobRunState']:
                break
        return response

    def check(self):
        crawler = self.glue_client.get_crawler('stepper-crawler-sh')
        crawler_status = crawler['Crawler']['LastCrawl']['Status']
        print('Crawler status - {}'.format(crawler_status))

if __name__ == '__main__':
    g = GlueProcessor()
    # g.get_crawler_status('stepper-crawler-sh')
    g.check()
