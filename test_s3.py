import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
import requests
import logging

# 配置日志

s3_client = boto3.client(
    "s3",
    endpoint_url='https://ewr1.vultrobjects.com',
    aws_access_key_id='TDQK4TPCI5O8GS5QSLY3',
    aws_secret_access_key='wygKl6u2sPdBvYEJYcICrvHXCBiORKUaxsGuC2Gb',
    region_name='eu-west-1',
)
def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response

def upload_file(signed_url, fields):
    # Ensure the file exists
    object_name = 'default_pic3.png'

    # Demonstrate how another Python program can use the presigned URL to upload a file
    with open('statics/default_pic3.png', 'rb') as f:
        files = {'file': (object_name, f, 'image/png')}
        http_response = requests.post(url=signed_url, data=fields, files=files)
        print(fields)
    # If successful, returns HTTP status code 204
    print(f'File upload HTTP status code: {http_response.status_code}')
    print(http_response.text)

def change_access_control(bucket_name):
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }

    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name, Policy=json.dumps(bucket_policy)
        )
        return True
    except ClientError as e:
        print(e)
        return False

def cors_configuration(bucket_name):
    cors_configuration = {
        "CORSRules": [
            {
                "AllowedHeaders": ["*"],  # 允许所有头部，或者你可以指定需要的头部
                "AllowedMethods": ["GET", "POST"],  # 现在包括了POST方法
                "AllowedOrigins": ["*"],  # 允许所有来源
                "ExposeHeaders": ["GET", "HEAD", "POST"],  # 允许浏览器接收的头部
                "MaxAgeSeconds": 3000
            }
        ]
    }

    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name, CORSConfiguration=cors_configuration
        )
        return True
    except ClientError as e:
        print(e)
        return False

if __name__=='__main__':
    bucket_name = 'cinegrade'
    # object_name = 'default_pic3.png'
    # response = create_presigned_post(bucket_name, object_name)
    # if response is not None:
    #     print(f"Generated POST URL: {response['url']}")
    #     print(f"Generated fields: {response['fields']}")
    #     upload_file(response['url'], response['fields'])
    # result=change_access_control(bucket_name)
    # print(result)
    result=cors_configuration(bucket_name)
    presigned_url = "https://ewr1.vultrobjects.com/cinegrade"
    fields = {
    "key": "test.png",
    "AWSAccessKeyId": "TDQK4TPCI5O8GS5QSLY3",
    "policy": "eyJleHBpcmF0aW9uIjogIjIwMjQtMDQtMTZUMTc6MjA6MzdaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAiY2luZWdyYWRlIn0sIHsia2V5IjogInRlc3QucG5nIn1dfQ==",
    "signature": "nViXN9OeLyDyPnPpn7hx0YGi2Q8="
  }
    # upload_file(presigned_url,fields)

