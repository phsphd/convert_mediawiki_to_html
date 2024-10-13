import boto3
import zipfile
import io
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Get the bucket and file (zip file) information
    bucket = event['Records'][0]['s3']['bucket']['name']
    zip_key = event['Records'][0]['s3']['object']['key']
    
    # Get the zip file from S3
    zip_obj = s3_client.get_object(Bucket=bucket, Key=zip_key)
    buffer = io.BytesIO(zip_obj['Body'].read())

    # Unzip the content
    with zipfile.ZipFile(buffer, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            file_info = zip_ref.getinfo(file_name)
            
            # If it's a file (not a directory)
            if not file_info.is_dir():
                # Read the file
                file_content = zip_ref.read(file_name)
                
                # Create the key for S3 (same directory structure as in the zip)
                new_file_key = file_name
                
                # Upload the extracted file back to S3
                s3_client.put_object(
                    Bucket=bucket,
                    Key=new_file_key,
                    Body=file_content
                )
    
    return {
        'statusCode': 200,
        'body': f"Successfully extracted {zip_key} in {bucket}"
    }
