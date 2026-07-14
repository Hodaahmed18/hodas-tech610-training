import boto3

s3 = boto3.client('s3')
s3.delete_object(Bucket='tech610-hoda-test-boto3', Key='testfile.txt')
