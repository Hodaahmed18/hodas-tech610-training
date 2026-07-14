import boto3

s3 = boto3.client('s3')
s3.create_bucket(
    Bucket='tech610-hoda-test-boto3',
    CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
)
