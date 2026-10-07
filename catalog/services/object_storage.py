"""Store article images on the OVH S3-compatible bucket."""

import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.config import Config

# Virtual-host bucket URL shown by OVH, for example
# https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net
_BUCKET_ENDPOINT = re.compile(
    r"^https://(?P<bucket>[a-z0-9][a-z0-9.-]*)\.s3\.(?P<region>[a-z0-9]+)\.io\.cloud\.ovh\.net/?$",
    re.IGNORECASE,
)
_UNSAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})


class ObjectStorageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class BucketEndpoint:
    bucket: str
    region: str
    public_base_url: str
    api_endpoint_url: str


def parse_bucket_endpoint(endpoint_url: str) -> BucketEndpoint:
    """Split an OVH bucket URL into the bucket, region, and API host."""
    match = _BUCKET_ENDPOINT.fullmatch(endpoint_url.strip())
    if match is None:
        raise ObjectStorageError(
            "L'endpoint OVH doit ressembler à https://nom-du-bucket.s3.rbx.io.cloud.ovh.net."
        )
    bucket = match.group("bucket").lower()
    region = match.group("region").lower()
    return BucketEndpoint(
        bucket=bucket,
        region=region,
        public_base_url=f"https://{bucket}.s3.{region}.io.cloud.ovh.net",
        api_endpoint_url=f"https://s3.{region}.io.cloud.ovh.net",
    )


def article_image_key(filename: str) -> str:
    """Build a unique object key from an uploaded file name."""
    cleaned = _UNSAFE_NAME.sub("-", Path(filename.replace("\\", "/")).name).strip(".-")
    if not cleaned:
        raise ObjectStorageError("Le nom de fichier de l'image est invalide.")
    return f"articles/{uuid4().hex}-{cleaned}"


def object_key(reference: str, *, public_base_url: str) -> str:
    """Accept either an object key or the public URL of that object."""
    reference = reference.strip()
    prefix = f"{public_base_url.rstrip('/')}/"
    if reference.startswith(prefix):
        reference = reference.removeprefix(prefix)
    key = reference.lstrip("/")
    if not key or ".." in Path(key).parts:
        raise ObjectStorageError("La clé de l'objet est invalide.")
    return key


class ArticleImageStorage:
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        client=None,
    ) -> None:
        self.location = parse_bucket_endpoint(endpoint_url)
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self._client = client

    def client(self):
        if self._client is not None:
            return self._client
        if not self.access_key_id or not self.secret_access_key:
            raise ObjectStorageError(
                "Renseignez OVH_S3_ACCESS_KEY_ID et OVH_S3_SECRET_ACCESS_KEY "
                "pour envoyer une image."
            )
        # The API host is regional. Virtual-host addressing then targets the bucket URL.
        # Checksums stay off unless required: OVH rejects the extra headers boto3 adds by default.
        self._client = boto3.client(
            "s3",
            endpoint_url=self.location.api_endpoint_url,
            region_name=self.location.region,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(
                signature_version="s3v4",
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
                s3={"addressing_style": "virtual"},
            ),
        )
        return self._client

    def public_url(self, key: str) -> str:
        return f"{self.location.public_base_url}/{key.lstrip('/')}"

    def upload_article_image(self, *, filename: str, body: bytes, content_type: str) -> str:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ObjectStorageError("Le fichier doit être une image JPEG, PNG ou WebP.")
        if not body:
            raise ObjectStorageError("Le fichier image est vide.")
        key = article_image_key(filename)
        self.client().put_object(
            Bucket=self.location.bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )
        return self.public_url(key)

    def delete_article_image(self, reference: str) -> None:
        key = object_key(reference, public_base_url=self.location.public_base_url)
        self.client().delete_object(Bucket=self.location.bucket, Key=key)


def article_image_storage() -> ArticleImageStorage:
    from django.conf import settings

    return ArticleImageStorage(
        endpoint_url=settings.OVH_S3_ENDPOINT_URL,
        access_key_id=settings.OVH_S3_ACCESS_KEY_ID,
        secret_access_key=settings.OVH_S3_SECRET_ACCESS_KEY,
    )
