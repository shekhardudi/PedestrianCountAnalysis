import logging
import boto3
from botocore.exceptions import ClientError
import config
from botocore.exceptions import NoCredentialsError
import os


def upload(file_path, bucket):
    file_dir, file_name = os.path.split(file_path)
    with open(file_path, "rb") as f:
        response = s3.upload_fileobj(f,bucket,file_name)
    return response

if __name__ == '__main__':

    s3 = boto3.client('s3')
    # response = s3.list_buckets()
    # print('Existing buckets:')
    # for bucket in response['Buckets']:
    #     print(f'  {bucket["Name"]}')

    # res = upload(file_path='data/Pedestrian_Counting_System_-_Sensor_Locations.csv', bucket=config.bucket_source)
    # print(res)
    # res = upload(file_path='data/Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv', bucket=config.bucket_source)
    # print(res)

    res = upload(file_path='GlueJob.py', bucket="step-script-bucket-sh")
    print(res)
