import pytest

from catalog.services.object_storage import (
    ArticleImageStorage,
    ObjectStorageError,
    article_image_storage,
    parse_bucket_endpoint,
)

ENDPOINT = "https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net/"


class FakeS3:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def put_object(self, **kwargs) -> None:
        self.calls.append(("put", kwargs))

    def delete_object(self, **kwargs) -> None:
        self.calls.append(("delete", kwargs))


def _storage(client=None) -> ArticleImageStorage:
    return ArticleImageStorage(
        endpoint_url=ENDPOINT,
        access_key_id="access-key",
        secret_access_key="secret-key",
        client=client,
    )


def test_bucket_endpoint_exposes_the_public_url_and_the_regional_api():
    location = parse_bucket_endpoint(ENDPOINT)

    assert location.bucket == "hellotoutous-bucket"
    assert location.region == "rbx"
    assert location.public_base_url == "https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net"
    assert location.api_endpoint_url == "https://s3.rbx.io.cloud.ovh.net"


def test_upload_stores_the_image_and_returns_its_public_url():
    client = FakeS3()
    storage = _storage(client)

    url = storage.upload_article_image(
        filename="photos/bandana photo.png",
        body=b"png",
        content_type="image/png",
    )

    action, params = client.calls[0]
    assert action == "put"
    assert params["Bucket"] == "hellotoutous-bucket"
    assert params["ContentType"] == "image/png"
    assert params["Body"] == b"png"
    assert params["Key"].startswith("articles/")
    assert params["Key"].endswith("-bandana-photo.png")
    assert url == f"https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net/{params['Key']}"


def test_upload_rejects_a_file_that_is_not_an_image():
    with pytest.raises(ObjectStorageError) as exc:
        _storage(FakeS3()).upload_article_image(
            filename="notes.txt",
            body=b"hello",
            content_type="text/plain",
        )
    assert "JPEG" in exc.value.message


def test_delete_accepts_the_public_url():
    client = FakeS3()
    storage = _storage(client)
    url = "https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net/articles/photo.png"

    storage.delete_article_image(url)

    assert client.calls == [
        ("delete", {"Bucket": "hellotoutous-bucket", "Key": "articles/photo.png"})
    ]


def test_missing_credentials_are_refused_before_any_request():
    storage = ArticleImageStorage(
        endpoint_url=ENDPOINT,
        access_key_id="",
        secret_access_key="",
    )
    with pytest.raises(ObjectStorageError) as exc:
        storage.client()
    assert "OVH_S3_ACCESS_KEY_ID" in exc.value.message


def test_client_targets_the_regional_endpoint(monkeypatch):
    captured: dict = {}

    def fake_client(service, **kwargs):
        captured["service"] = service
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("catalog.services.object_storage.boto3.client", fake_client)
    _storage().client()

    assert captured["service"] == "s3"
    assert captured["endpoint_url"] == "https://s3.rbx.io.cloud.ovh.net"
    assert captured["region_name"] == "rbx"
    assert captured["aws_access_key_id"] == "access-key"
    assert captured["config"].s3["addressing_style"] == "virtual"


def test_storage_reads_its_configuration_from_settings():
    storage = article_image_storage()

    assert storage.location.bucket == "hellotoutous-bucket"
    assert storage.location.region == "rbx"
