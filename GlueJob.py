import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import col
from pyspark.sql.functions import to_date, split
from pyspark.sql import SQLContext
import pandas as pd
from io import StringIO

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glue_context = GlueContext(sc)
sqlCtx = SQLContext(sc)
# Init my job
job = Job(glue_context)
job.init(args['JOB_NAME'], args)
dynamic_frame_steps = glue_context.create_dynamic_frame.from_catalog(database='step-count-analysis-sh', table_name='pedestrian_counting_system___monthly__counts_per_hour__csv',
                                                               transformation_ctx="datasource0")
                                                               
dynamic_frame_sensor = glue_context.create_dynamic_frame.from_catalog(database='step-count-analysis-sh', table_name='pedestrian_counting_system___sensor_locations_csv',
                                                               transformation_ctx="datasource0")
                                                               
df = dynamic_frame_steps.toDF()
df_cph = df.toPandas()

df1 = dynamic_frame_sensor.toDF()
df_sensor = df1.toPandas()

df_cph['date'] = pd.to_datetime(df_cph['date_time'])
df_cph['step_counts'] = df_cph['hourly_counts'].str.split(',').str.join('').astype(int)

df_Monthly = df_cph.groupby([ pd.Grouper(key='date', freq='M'),'sensor_id'])['step_counts'].sum().reset_index(drop=False)
df_Monthly = df_Monthly.groupby('date').apply(lambda x: x.sort_values('step_counts',ascending=False).head(10)).reset_index(drop=True)

df_Monthly = df_Monthly.merge(df_sensor,on='sensor_id',how='left')


df_Daily = df_cph.groupby([ pd.Grouper(key='date', freq='D'),'sensor_id'])['step_counts'].sum().reset_index(drop=False)
df_Daily = df_Daily.groupby('date').apply(lambda x: x.sort_values('step_counts',ascending=False).head(10)).reset_index(drop=True)

df_Daily = df_Daily.merge(df_sensor,on='sensor_id',how='left')

mdf = sqlCtx.createDataFrame(df_Monthly.reset_index(drop=False))
ddf = sqlCtx.createDataFrame(df_Daily.reset_index(drop=False))

transform1 = DynamicFrame.fromDF(
    mdf, glue_context, 'transform1')
transform2 = DynamicFrame.fromDF(
    ddf, glue_context, 'transform2')

repartition_m = transform1.repartition(1)
repartition_d = transform2.repartition(1)
    
datasink1 = glue_context.write_dynamic_frame.from_options(frame=repartition_m, connection_type="s3", connection_options={
                                                         "path": 's3://step-count-output-bucket-sh/monthly'}, format="csv", transformation_ctx="datasink1")
datasink2 = glue_context.write_dynamic_frame.from_options(frame=repartition_d, connection_type="s3", connection_options={
                                                         "path": 's3://step-count-output-bucket-sh/daily'}, format="csv", transformation_ctx="datasink2")
                                                         
print("Dynamic frame saved in s3")

datasink3 = glue_context.write_dynamic_frame.from_jdbc_conf(frame = repartition_m, catalog_connection = "PostGresConSh", connection_options = {"dbtable":"monthly","database":"MyDB"}, transformation_ctx="datasink1")
datasink3 = glue_context.write_dynamic_frame.from_jdbc_conf(frame = repartition_d, catalog_connection = "PostGresConSh", connection_options = {"dbtable":"daily","database":"MyDB"}, transformation_ctx="datasink2")




# # Commit file read to Job Bookmark
job.commit()
print("Job completed!!!")