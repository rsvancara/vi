import boto3
from visualintrigue import siteconfig







def main():


    
    s3 = boto3.resource('s3',aws_access_key_id=siteconfig.AMAZON_KEY, aws_secret_access_key=siteconfig.AMAZON_SECRET)
    data = open('/Users/rsvancara/Pictures/backgrounds/rattlesnake_lake.jpg', 'rb')
    s3.Bucket(siteconfig.AMAZON_BUCKET).put_object(Key='rattlesnake_lake.jpg    ', Body=data, ContentType='image/jpeg')
    data.close()
    
    # 
    # 
    # conn = S3Connection(siteconfig.AMAZON_KEY,siteconfig.AMAZON_SECRET)
    # 
    # rs = conn.get_all_buckets()
    # 
    # for i in rs:
    #     print(i.name)
    # 
    # 
    # abucket = conn.get_bucket("s3://" + siteconfig.AMAZON_BUCKET)
    # 
    # akey = Key(abucket)
    # 
    # akey.set_contents_from_filename('/Users/rsvancara/Pictures/backgrounds/rattlesnake_lake.jpg')

if __name__ == '__main__':
    
    main()
    