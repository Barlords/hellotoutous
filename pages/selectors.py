from catalog.selectors import list_categories
from contact.forms import ContactForm
from contact.services.form_token import current_token

# Studio shots used as category tiles on the homepage.
CATEGORY_IMAGES = {
    "collar": "img/accessory/collier.png",
    "harness": "img/accessory/harnais.png",
    "leash": "img/accessory/laisse.png",
    "bandana": "img/accessory/bandana.png",
    "bag_dispenser": "img/accessory/distributeur.png",
    "treat_pouch": "img/accessory/sacafriandise.png",
    "bow": "img/accessory/noeud.png",
}


def home_context(request, form: ContactForm) -> dict:
    success = request.session.pop("contact_success", False)
    if success:
        request.session.modified = True
    categories = list_categories()
    for category in categories:
        category.presentation_image = CATEGORY_IMAGES.get(category.code, "")
    return {
        "page_title": "Accueil",
        "categories": categories,
        "form": form,
        "contact_token": current_token(request.session),
        "contact_success": success,
    }
