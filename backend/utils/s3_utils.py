import json
import boto3
import botocore

client = boto3.client('s3', config=botocore.client.Config(max_pool_connections=50))


def upload_file_to_s3(body, file_name, bucket_name, directory=None):
    filename_s3 = f"{directory}/{file_name}" if directory else file_name
    client.put_object(Body=body, Bucket=bucket_name, Key=filename_s3)


def download_from_s3(file_name, bucket_name, directory=None):
    filename_s3 = f"{directory}/{file_name}" if directory else file_name
    obj = client.get_object(Bucket=bucket_name, Key=filename_s3)
    return obj['Body'].read().decode('utf-8')
