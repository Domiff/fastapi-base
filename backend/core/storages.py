import io
from functools import lru_cache
from typing import BinaryIO

from fastapi_storages import S3Storage as BaseS3Storage

from backend.core.config import settings


class S3Storage(BaseS3Storage):
    AWS_ACCESS_KEY_ID = settings.storage.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.storage.AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME = settings.storage.AWS_S3_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = settings.storage.AWS_S3_ENDPOINT_URL
    AWS_DEFAULT_ACL = settings.storage.AWS_DEFAULT_ACL
    AWS_S3_USE_SSL = settings.storage.AWS_S3_USE_SSL

    def open(self, name: str) -> BinaryIO:
        buffer = io.BytesIO()
        self._s3.download_fileobj(self.AWS_S3_BUCKET_NAME, self.get_name(name), buffer)
        buffer.seek(0)
        return buffer


@lru_cache
def get_storage() -> S3Storage:
    """Клиент создаётся при первом обращении: без него приложение стартует и без S3."""
    return S3Storage()
