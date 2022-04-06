import boto3 as boto3
import csv, io
import random

from config import Config


def save_to_storage(data: dict, key_name: str) -> str:

    session = boto3.session.Session()

    s3 = session.client(
        service_name=Config.S3_SERVICE_NAME,
        endpoint_url=Config.S3_ENDPOINT_URL,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )
    
    key_name = f'{key_name}.csv'    
    
    # Check for key already exists in the backet
    if 'Contents' in s3.list_objects(Bucket=Config.S3_BACKET_ID):
        keys = [key['Key'] for key in s3.list_objects(Bucket=Config.S3_BACKET_ID)['Contents']]
    
        if key_name in keys:
            return key_name
    
    # csv module can write data in io.StringIO buffer only
    s = io.StringIO()
    csv.writer(s).writerows(data.items())
    s.seek(0)

    # convert it to bytes and write to buffer
    buf = io.BytesIO()
    buf.write(s.getvalue().encode())
    buf.seek(0)

    s3.upload_fileobj(buf, Bucket=Config.S3_BACKET_ID, Key=key_name)

    return key_name
