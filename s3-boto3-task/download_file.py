import boto3

s3 = boto3.client('s3')
s3.download_file('tech610-hoda-test-boto3', 'testfile.txt', 'downloaded_testfile.txt')
