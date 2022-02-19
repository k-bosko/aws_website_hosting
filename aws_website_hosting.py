import boto3
import os
import requests
import zipfile
import io

def upload_directory(path, bucketname, s3):
    for root, dirs, files in os.walk(path):
        for file in files:
            s3.meta.client.upload_file(os.path.join(root,file),bucketname,file)

def main():
    site_path = 'aws_website_hosting'
    if not os.path.exists(site_path):
        os.mkdir(site_path)

    # get the data from link
    url = "https://github.com/k-bosko/aws_website_hosting/archive/refs/heads/main.zip"
    r = requests.get(url, stream=True)
    # unzip it
    with zipfile.ZipFile(io.BytesIO(r.content), 'r') as zip_ref:
        zip_ref.extractall(site_path)

    # access ressource and name it s3
    s3 = boto3.resource('s3')
    bucket_name = 'lab1-kbosko'

    #list buckets
    buckets = s3.buckets.all()

    #delete if bucket with this name exists
    if s3.Bucket(bucket_name) in buckets:
        s3.delete_bucket(Bucket='lab1-kbosko', )

    #create bucket
    s3.create_bucket(Bucket=bucket_name)

    # print existing bucket names for debugging
    for bkt in buckets:
        print(bkt.name)

    #copy files to s3
    upload_directory(site_path, bucket_name, s3)

    #instantiate bucket
    bucket = s3.Bucket(bucket_name)

    #update permission
    bucket.Acl().put(ACL='public-read')


if __name__ == '__main__':
    main()
