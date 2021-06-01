from Process.Glue import Glue
from CountingSystem.S3 import S3
import config
import os

def upload_required_data():

    res = s3_obj.upload(file_path=os.path.join('data','Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv'),
                    bucket=config.source_data_bucket)
    if res:
        print('Pedestrian Count Csv upload successful')

        res = s3_obj.upload(file_path=os.path.join('data','Pedestrian_Counting_System_-_Sensor_Locations.csv'),
                bucket=config.source_data_bucket)
        if res:
            print('Sensor data uploaded successfully')
        else:
            print('Sensor upload failed. Can not continue')
            exit(1)
    else:
        print('Pedestrian count upload failed. Can not continue')
        exit(1)

    res = s3_obj.upload(file_path='GlueJob.py',
                bucket=config.script_bucket)
    if res:
        print('Glue Script uploaded successfully')
    else:
        print('Glue Script upload failed. Can not continue')
        exit(1)

def run_crawler():
    glue_obj.run_crawler(config.crawler_name)
    status = glue_obj.get_crawler_status(config.crawler_name)

    if status:
        print('Crawler Run Complete')
    else:
        print('Could not catalog data')
        exit(1)  

def run_glue_job():
    job_run = glue_obj.run_job(config.glue_job_name)
    resp = glue_obj.get_job_status(job_name= config.glue_job_name,job_run=job_run)
    if resp:
        print("Glue Job finished Successfully!")
    else:
        print("Glue Job Failed")

if __name__ == '__main__':
    s3_obj = S3()
    glue_obj = Glue()

    print("Process Started")
    
    upload_required_data()
    run_crawler()
    run_glue_job()





