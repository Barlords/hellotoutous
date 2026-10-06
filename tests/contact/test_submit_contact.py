import pytest
from django.core import mail

from contact.models import ContactMessage
from contact.services.submit_contact import ContactDeliveryError, ContactPayload, submit_contact

pytestmark = pytest.mark.django_db


def _payload() -> ContactPayload:
    return ContactPayload(
        name="Camille",
        email="camille@example.com",
        city="Lyon",
        category="custom_order",
        category_label="Demande sur mesure",
        message="Un collier rouge pour un beagle.",
    )


def test_submit_saves_and_sends_to_hello_toutous():
    submit_contact(_payload(), recipient="hellotoutous@hotmail.com")

    stored = ContactMessage.objects.get()
    assert stored.category == "custom_order"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["hellotoutous@hotmail.com"]
    assert "Demande sur mesure" in mail.outbox[0].body
    assert "Un collier rouge pour un beagle." in mail.outbox[0].body


def test_failed_email_does_not_keep_the_message(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("smtp down")

    monkeypatch.setattr("contact.services.submit_contact.send_mail", boom)

    with pytest.raises(ContactDeliveryError):
        submit_contact(_payload(), recipient="hellotoutous@hotmail.com")
    assert ContactMessage.objects.count() == 0
