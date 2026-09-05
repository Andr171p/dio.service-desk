import logging

from botocore.exceptions import ClientError

from src.media.infra.s3 import S3Storage

logger = logging.getLogger(__name__)


async def main() -> None:
    storage = S3Storage(
        endpoint_url=...,
        access_key=...,
        secret_key=...,
        bucket_name=...,
    )

    async with storage.get_client() as client:
        try:
            await client.head_bucket(Bucket=...)
            logger.info("S3 bucket=`%s` already exists, skipping creation", ...)
        except ClientError:
            logger.info("S3 bucket does not exist, start creating - `%s`", ...)
            await client.create_bucket(Bucket=...)

    logger.info("S3 bucket=%s created successfully", ...)
