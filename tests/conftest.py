import pytest


@pytest.fixture(autouse=True)
def email_backend(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
