import io
import boto3
from django.conf import settings

class S3():
    '''AWS and compatible operations using boto3'''

    def __init__(self, bucket):

        self.bucket = bucket 

        self.resource = self._s3_resource()

        self.client = self._s3_client()


    def _s3_resource(self):
        '''boto3 connection. 
        return resource for use in Bucket operations etc.'''

        return boto3.resource(
            's3',
            endpoint_url = settings.AWS_S3_CUSTOM_DOMAIN,
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY 
        )


    def _s3_client(self):
        '''boto3 connection. 
        return client for use in query operations etc.'''

        return boto3.client(
            's3',
            endpoint_url = settings.AWS_S3_CUSTOM_DOMAIN,
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY 
        )


    def get_presigned_url(self, file_name, expire=2400):
        '''generate presigned temp url for resource
            :param str file_name: name of resource
            :param int expire: seconds until temp url expires. 
            :return: str url''' 

        return self.client.generate_presigned_url('get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': file_name},
                ExpiresIn=expire)


    def get_presigned_download_url(self, file_name, expire=2400): 
        '''generate presigned temp url for resource.
            this will download.
            :param str file_name: name of resource
            :param int expire: seconds until temp url expires. 
            :return: str url''' 

        return self.client.generate_presigned_url('get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': file_name,
                    'ResponseContentDisposition': 'attachment; filename=%s' % file_name
                    },
                ExpiresIn=expire)


    def save_to_bucket(self, name, file_):
        '''save file to bucket. 
            :param str name
            :param object file_
            :return: None''' 

        self.resource.Bucket(self.bucket).put_object(Key=name, Body=file_)


    def delete_from_bucket(self, name):
        '''delete file from bucket. 
            :param str name
            :return: None''' 
        
        self.resource.Object(self.bucket, name).delete()


    def download_fileobj_from_bucket(self, name):
        '''download file from bucket. 
            :param str name
            :return: memory file object (io.BytesIO)''' 

        s3_obj = self.resource.Object(self.bucket, name)
        fakefile = io.BytesIO()
        s3_obj.download_fileobj(fakefile)

        return fakefile
