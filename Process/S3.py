import pandas as pd
import os
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import time
from CountingSystem import config


class S3:

    def __init__(self):
        self.s3 = boto3.client('s3')

    def upload(self, file_path, bucket):
        file_dir, file_name = os.path.split(file_path)
        try:
            with open(file_path, "rb") as f:
                self.s3.upload_fileobj(f,bucket,file_name)
        except Exception as e:
            print("Exception in uploading the file to S3")
            print(e)
            return False
        return True

    def delete_all_obj(self, bucket_name):

        response = self.s3.list_objects_v2(
            Bucket=bucket_name,
        )

        while response['KeyCount'] > 0:
            print('Deleting %d objects from bucket %s' % (len(response['Contents']),bucket_name))
            response = self.s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects':[{'Key':obj['Key']} for obj in response['Contents']]
                }
            )
            response = self.s3.list_objects_v2(
                Bucket=bucket_name,
            )

if __name__ == '__main__':
    s = S3()
    s.delete_all_obj(config.script_bucket)
    s.delete_all_obj(config.source_data_bucket)
    s.delete_all_obj(config.output_data_bucket)
