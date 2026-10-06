from catalog.selectors import list_categories
from contact.forms import ContactForm
from contact.services.form_token import current_token


def home_context(request, form: ContactForm) -> dict:
    success = request.session.pop("contact_success", False)
    if success:
        request.session.modified = True
    return {
        "page_title": "Accueil",
        "categories": list_categories(),
        "form": form,
        "contact_token": current_token(request.session),
        "contact_success": success,
    }
