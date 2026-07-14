import boto3

s3 = boto3.client('s3')
s3.upload_file('testfile.txt', 'tech610-hoda-test-boto3', 'testfile.txt')
