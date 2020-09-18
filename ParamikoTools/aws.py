import boto3
import botocore
import os

import sys

from s3fs.core import S3FileSystem

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id='AKIATRKG6IWFCIRMA5YC',
    aws_secret_access_key='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'
)

s3_file = S3FileSystem()


# Download file and read from disc

def download_file(bucket, key, filename):
    try:
        s3.Bucket(bucket).download_file(Key=key, Filename=filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def upload_file(bucket, key, filename):
    try:
        s3.Bucket(bucket).upload_file(Key=key, Filename=filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
