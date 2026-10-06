from django import forms

from contact.copy import INVALID_EMAIL, REQUIRED
from contact.models import MessageCategory


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Nom",
        max_length=120,
        error_messages={"required": REQUIRED},
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Courriel",
        error_messages={"required": REQUIRED, "invalid": INVALID_EMAIL},
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    city = forms.CharField(
        label="Ville",
        max_length=120,
        error_messages={"required": REQUIRED},
        widget=forms.TextInput(attrs={"autocomplete": "address-level2"}),
    )
    category = forms.ChoiceField(
        label="Catégorie du message",
        choices=MessageCategory.choices,
        error_messages={"required": REQUIRED, "invalid_choice": REQUIRED},
    )
    message = forms.CharField(
        label="Message",
        error_messages={"required": REQUIRED},
        widget=forms.Textarea(attrs={"rows": 6}),
    )
