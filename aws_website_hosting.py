import boto3
import os
import requests
import zipfile
import io
import json


def upload_directory(path, bucketname, client):
    print("starting upload")
    for root, dirs, files in os.walk(path):
        for file in files:
            relative_path = os.path.join(root, file)
            path_to_upload = relative_path.replace('aws_website_hosting-main/', '')
            print("uploading: ", path_to_upload)
            extension = file.split('.')[-1]
            mode = 'rb' if extension in {'png', 'ico', 'jpg', 'pdf'} else 'r'

            if extension == 'html':
                content_type = 'text/html'
            elif extension == 'css':
                content_type = 'text/css'
            elif extension == 'js':
                content_type = 'application/javascript'
            elif extension == 'pdf':
                content_type = 'application/pdf'
            elif extension == 'jpg':
                content_type = 'image/jpeg'
            elif mode == 'r':
                content_type = 'text/plain'
            else:
                content_type = 'binary/octet-stream'

            with open(relative_path, mode=mode) as fp:
                params = {
                    'Bucket': bucketname,
                    'Body': fp.read(),
                    'Key': path_to_upload,
                    'ContentType': content_type,
                }
                client.put_object(**params)


def main():
    if not os.path.isdir('aws_website_hosting-main'):
        # get the data from link
        url = "https://github.com/k-bosko/aws_website_hosting/archive/refs/heads/main.zip"
        r = requests.get(url, stream=True)
        # unzip it
        with zipfile.ZipFile(io.BytesIO(r.content), 'r') as zip_ref:
            zip_ref.extractall()

    # create s3 resource
    s3 = boto3.resource('s3')
    # create a client
    client = boto3.client('s3')

    bucket_name = 'lab1kbosko'
    site_path = 'aws_website_hosting-main'

    #list buckets
    buckets = s3.buckets.all()

    #delete if bucket with this name exists
    bucket_to_delete = s3.Bucket(bucket_name)
    if bucket_to_delete in buckets:
        print(f"deleting existing bucket `{bucket_name}`")
        bucket_to_delete.Acl().put(ACL='public-read-write')
        bucket_to_delete.objects.all().delete()
        bucket_to_delete.delete()

    #create bucket with public-read permission
    s3.create_bucket(ACL='public-read', Bucket=bucket_name)

    # print existing bucket names for debugging
    for bkt in buckets:
        print(bkt.name)

    #add website configuration to a bucket
    client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {
                'Suffix': 'index.html',
            },
        },
    )

    policy = { "Version": "2012-10-17", "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

    #add bucket policy
    client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(policy),
    )

    #copy files to s3
    upload_directory(site_path, bucket_name, client)

if __name__ == '__main__':
    main()
