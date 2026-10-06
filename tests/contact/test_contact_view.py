import pytest
from django.core import mail

from contact.models import ContactMessage

pytestmark = pytest.mark.django_db


def _post(client, **overrides):
    page = client.get("/")
    token = page.context["contact_token"]
    data = {
        "form_token": token,
        "name": "Camille",
        "email": "camille@example.com",
        "city": "Lyon",
        "category": "customer_review",
        "message": "Très belle finition.",
    }
    data.update(overrides)
    return client.post("/contact/", data)


def test_invalid_email_is_explained_next_to_the_field(client):
    response = _post(client, email="pas-un-courriel")
    html = response.content.decode()

    assert response.status_code == 422
    assert "Saisissez une adresse courriel valide." in html
    assert 'aria-invalid="true"' in html
    assert 'role="alert"' in html
    assert ContactMessage.objects.count() == 0


def test_success_redirects_and_refresh_does_not_send_again(client):
    response = _post(client)
    assert response.status_code == 302
    assert response["Location"].endswith("/#contact")

    follow = client.get("/")
    assert "Votre message a bien été envoyé." in follow.content.decode()
    assert 'role="status"' in follow.content.decode()
    assert ContactMessage.objects.count() == 1
    assert len(mail.outbox) == 1

    client.get("/")
    assert ContactMessage.objects.count() == 1
    assert len(mail.outbox) == 1


def test_reusing_a_token_does_not_send_again(client):
    page = client.get("/")
    token = page.context["contact_token"]
    data = {
        "form_token": token,
        "name": "Camille",
        "email": "camille@example.com",
        "city": "Lyon",
        "category": "other",
        "message": "Bonjour",
    }
    assert client.post("/contact/", data).status_code == 302
    assert client.post("/contact/", data).status_code == 302
    assert ContactMessage.objects.count() == 1
    assert len(mail.outbox) == 1
