from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

from asset.constants import DEFAULT_PRESIGNED_URL_EXPIRY
from asset.exceptions import S3Error
from core.exceptions import catch_and_reraise


@dataclass(frozen=True)
class S3ObjectMetadata:
    content_type: str
    content_length: int
    etag: str | None = None


def get_s3_client():
    return boto3.client('s3')


def head_object(
    bucket_name: str,
    object_name: str,
) -> S3ObjectMetadata | None:
    s3_client = get_s3_client()
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
        return S3ObjectMetadata(
            content_type=response.get(
                'ContentType',
                'application/octet-stream',
            ),
            content_length=response.get('ContentLength', 0),
            etag=response.get('ETag'),
        )
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        raise S3Error(
            message=f'Failed to get object metadata from S3: {e}',
        ) from e


def generate_presigned_put_url(
    bucket_name: str,
    object_name: str,
    content_type: str,
    expiration: int = DEFAULT_PRESIGNED_URL_EXPIRY,
) -> str:
    s3_client = get_s3_client()
    with catch_and_reraise(
        ClientError,
        S3Error,
        'Failed to generate presigned URL',
    ):
        return s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                'ContentType': content_type,
            },
            ExpiresIn=expiration,
        )
