import os
from urllib.parse import urlsplit, urljoin

from boto3 import Session
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from django_s3_storage.storage import S3Storage

from common.core.settings import project_settings, BaseSection
from common.utils.datetime import FILENAME_FORMAT, datetime_to_str
from common.utils.static import DEFAULT_FILES

__all__ = [
    'ReplaceFileStorage',
    'BaseS3Storage',
    'UnReadingS3Storage',
    'UncachedS3Storage',
    'replace_filestorage',
    's3_storage',
    'uncached_s3_storage',
    'makeup_s3_url',
    'get_s3_bucket'
]


class ReplaceFileStorage(FileSystemStorage):
    """
    覆盖图片的本地存储
    """

    def get_available_name(self, name, max_length=None):
        """
        默认行为是保留重名文件，将新文件重新命名
        这里在保存前删除旧文件，可允许将新文件保存成原来的名字
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class BaseS3Storage(S3Storage):
    """
    基础存储

    修复图片保存失败问题等
    """

    def path(self, name):
        return

    def _save(self, name, content):
        """
        Create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload whereas the storage backend expects it to still be open
        """
        content.seek(0, os.SEEK_SET)

        # Create a new temporary file in order to solve close file issue
        new_content = NamedTemporaryFile()
        new_content.write(content.read())

        name = super()._save(name, new_content)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not new_content.closed:
            new_content.close()

        return name


class UnReadingS3Storage(BaseS3Storage):
    """
    默认存储

    请求获取url时本地组合url地址，不读取s3服务器
    """

    def url(self, name, extra_params=None, **kwargs):
        if not name:
            name = DEFAULT_FILES.default_image
        url = makeup_s3_url(
            name, endpoint_url=self.settings.AWS_S3_ENDPOINT_URL,
            bucket_name=self.settings.AWS_S3_BUCKET_NAME)
        return url


class UncachedS3Storage(BaseS3Storage):
    """
    非缓存存储

    时间参数（默认按分钟刷新）
    """

    def __init__(self, datetime_format=None, **kwargs):
        self._fmt = datetime_format or FILENAME_FORMAT
        super().__init__(**kwargs)

    @property
    def datetime_format(self):
        return self._fmt

    @datetime_format.setter
    def datetime_format(self, fmt):
        self._fmt = fmt

    def url(self, name, extra_params=None, **kwargs):
        url = super().url(name, extra_params=extra_params)
        split_result = urlsplit(url)
        query_value = datetime_to_str(timezone.now(), fmt=self.datetime_format)
        query = f'_={query_value}'
        qs = '&' if split_result.query else '?'
        url += qs + query
        return url


def makeup_s3_url(obj_key, endpoint_url=None, bucket_name=None):
    """
    根据name，组合s3的url，适用于阿里云oss
    """
    if not endpoint_url or not bucket_name:
        endpoint_url = project_settings.storage.endpoint_url
        bucket_name = project_settings.storage.bucket_name
    return urljoin(
        endpoint_url,
        os.path.join(bucket_name, obj_key)
    )


def get_s3_bucket(storage_section: BaseSection = project_settings.storage):
    """
    默认获取项目默认存储
    """
    session = Session(
        aws_access_key_id=storage_section.access_key,
        aws_secret_access_key=storage_section.secret_key
    )
    s3_bucket = session.resource(
        's3', endpoint_url=storage_section.endpoint_url
    ).Bucket(storage_section.bucket_name)
    return s3_bucket


replace_filestorage = ReplaceFileStorage()
base_s3_storage = BaseS3Storage(aws_s3_bucket_name=project_settings.storage.bucket_name)
s3_storage = UnReadingS3Storage(aws_s3_bucket_name=project_settings.storage.bucket_name)
uncached_s3_storage = UncachedS3Storage(aws_s3_bucket_name=project_settings.storage.bucket_name)
