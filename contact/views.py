from django.conf import settings
from django.shortcuts import redirect, render

from contact.copy import EMAIL_FAILED
from contact.forms import ContactForm
from contact.models import MessageCategory
from contact.services.form_token import consume_token, issue_token
from contact.services.submit_contact import ContactDeliveryError, ContactPayload, submit_contact
from pages.selectors import home_context


def submit_contact_view(request):
    if request.method != "POST":
        return redirect("/#contact")
    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, "pages/home.html", home_context(request, form), status=422)
    if not consume_token(request.session, request.POST.get("form_token", "")):
        return redirect("/#contact")
    label = dict(MessageCategory.choices)[form.cleaned_data["category"]]
    payload = ContactPayload(
        name=form.cleaned_data["name"],
        email=form.cleaned_data["email"],
        city=form.cleaned_data["city"],
        category=form.cleaned_data["category"],
        category_label=label,
        message=form.cleaned_data["message"],
    )
    try:
        submit_contact(payload, recipient=settings.CONTACT_RECIPIENT_EMAIL)
    except ContactDeliveryError:
        issue_token(request.session)
        form.add_error(None, EMAIL_FAILED)
        return render(request, "pages/home.html", home_context(request, form), status=422)
    request.session["contact_success"] = True
    return redirect("/#contact")
