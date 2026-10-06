from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail

from contact.models import ContactMessage


class ContactDeliveryError(Exception):
    pass


@dataclass(frozen=True)
class ContactPayload:
    name: str
    email: str
    city: str
    category: str
    category_label: str
    message: str


def submit_contact(payload: ContactPayload, *, recipient: str) -> ContactMessage:
    stored = ContactMessage.objects.create(
        name=payload.name,
        email=payload.email,
        city=payload.city,
        category=payload.category,
        message=payload.message,
    )
    body = "\n".join(
        [
            f"Nom : {payload.name}",
            f"Courriel : {payload.email}",
            f"Ville : {payload.city}",
            f"Catégorie : {payload.category_label}",
            "",
            payload.message,
        ]
    )
    try:
        send_mail(
            subject="Nouveau message — Hello Toutous",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception as exc:
        stored.delete()
        raise ContactDeliveryError from exc
    return stored
