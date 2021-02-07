import json
import logging
import os
import boto3
from typing import List, Optional, Text, Tuple

logger = logging.getLogger(__name__)


class AWSPersistor:
    """Store models on S3.
    Fetches them when needed, instead of storing them on the local disk."""

    def __init__(self, bucket_name: Text, region_name: Optional[Text] = 'cn-northwest-1') -> None:
        super().__init__()
        self.s3 = boto3.resource("s3", region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self._ensure_bucket_exists(bucket_name)
        self.bucket_name = bucket_name
        self.bucket = self.s3.Bucket(bucket_name)

    def download(self, s3_file, local_file):
        local_dir = os.path.dirname(local_file)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        with open(local_file, "wb") as f:
            self.bucket.download_fileobj(s3_file, f)

    def download_directory(self, s3_dir, local_dir):
        keys = {local_dir.rstrip('/')}
        for object in self.bucket.objects.filter(Prefix=s3_dir):
            fname = object.key[len(s3_dir):].lstrip('/')
            if fname.rstrip('/') not in keys:
                if fname.endswith('/'):
                    self.download_directory(object.key, fname)
                elif fname:
                    self.download(object.key, os.path.join(local_dir, fname))
                keys.add(fname.rstrip('/'))

    def _ensure_bucket_exists(self, bucket_name) -> None:
        import botocore

        try:
            self.s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                raise FileNotFoundError(bucket_name)

    def upload(self, local_file: Text, s3_file: Text) -> None:
        with open(local_file, "rb") as f:
            self.s3.Object(self.bucket_name, s3_file).put(Body=f)


if __name__ == '__main__':
    # persistor = AWSPersistor('mesoor-ocr')
    test_json = {'test': 123}
    local_json_file_path = './test_json_file.json'
    with open(local_json_file_path, 'w') as json_file_writer:
        json.dump(test_json, json_file_writer, ensure_ascii=False)

    # persistor.upload(local_json_file_path, '58tongcheng/test.json')

