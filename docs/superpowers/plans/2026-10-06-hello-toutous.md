# Hello Toutous — plan d'implémentation (itération 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Livrer la page d'accueil Hello Toutous, le formulaire de contact, l'admin catalogue et un compteur de panier en session, sans tunnel de paiement.

**Architecture:** Django sert des pages HTML. Les règles métier (option nœud, prix, panier, envoi du contact) vivent dans des services sans `request` ni template. Les vues assemblent le contexte et choisissent le retour affiché. Les modèles persiste et délèguent la validation aux services. Le JavaScript se limite au carrousel.

**Tech Stack:** Python 3.12, uv, Django 5.2 LTS, templates Django, CSS et JavaScript sans framework, pytest + pytest-django, SQLite, e-mail Django.

Le guide des tailles, la galerie, la liste par catégorie, la fiche article et Stripe ne font pas partie de ce plan. Leurs URLs répondent déjà, avec une page « à venir ».

## Global Constraints

- Textes visibles en français. Noms de tables, de champs, de modules et commentaires de code en anglais.
- Couleurs : bandeau et boutons `#D46A54`, fond `#FEA674`, seconde couleur du dégradé `#FEBC97`, titres `#6C4F3E`, texte courant `#3F2A22`, texte des boutons et du bandeau blanc, navbar `#FFF6F0`.
- Dégradé vertical du haut vers le bas, de `#FEA674` vers `#FEBC97`.
- Titres en Fraunces. Texte, navigation, boutons et formulaire en Source Sans 3.
- Menu, dans cet ordre : Boutique, Notre histoire, Guide des tailles, Galerie, Contact. Puis le panier à droite.
- Notre histoire pointe vers `/#notre-histoire`. Contact pointe vers `/#contact`. Les deux URLs fonctionnent depuis n'importe quelle page.
- Boutique, guide des tailles, galerie et panier sont des pages « à venir ».
- Le compteur du panier est le total des quantités. « Avec nœud » ne crée pas une seconde ligne.
- « Avec nœud » seulement pour les catégories `collar` et `harness`. Le supplément `knot_price` est strictement positif quand l'option est active, et vide quand elle ne l'est pas.
- Un article a plusieurs variantes taille + couleur. Une seule variante par couple taille + couleur.
- Contact enregistré en base et envoyé à `hellotoutous@hotmail.com`. Recharger la page après succès n'enregistre pas un second message.
- Pied de page : téléphone `06 46 56 54 20` (lien `tel:+33646565420`), e-mail `hellotoutous@hotmail.com`, mention `© Company 2026`.
- Instagram est écrit dans la phrase de contact, sans lien.
- `LANGUAGE_CODE` = `fr-fr`. `TIME_ZONE` = `Europe/Paris`.
- Dépendances et commandes via uv. `uv.lock` est versionné. Pas de `pip`, pas de venv créé à la main. Tests : `uv run pytest`. Lint : `uv run ruff check`. Django : `uv run python manage.py`.

## Structure des fichiers

Chaque fichier a une seule raison de changer.

```text
manage.py
pyproject.toml
uv.lock
.gitignore
config/settings.py          # réglages du projet
config/urls.py              # branchement des URLs, rien d'autre
catalog/models.py           # persistance du catalogue
catalog/admin.py            # présentation admin
catalog/selectors.py        # lectures
catalog/services/knot_rules.py
catalog/services/pricing.py
catalog/services/add_to_cart.py
catalog/migrations/0002_seed_references.py
cart/services/session_cart.py
cart/context_processors.py
contact/models.py
contact/forms.py
contact/copy.py             # phrases affichées, un seul endroit
contact/services/form_token.py
contact/services/submit_contact.py
contact/views.py
pages/selectors.py
pages/views.py
pages/urls.py
templates/base.html
templates/includes/navbar.html
templates/includes/footer.html
templates/pages/home.html
templates/pages/coming_soon.html
static/css/site.css
static/js/carousel.js
tests/...
```

`catalog.services.pricing` ne importe pas les modèles. `session_cart` ne connaît pas les produits. `add_to_cart` est le seul endroit qui relie un article au panier. `submit_contact` enregistre puis envoie l'e-mail. Les vues ne calculent pas un prix et n'appellent pas `send_mail`.

---

### Task 1: Socle du projet

**Files:**
- Create: `pyproject.toml`
- Create: `uv.lock`
- Create: `.python-version`
- Create: `.gitignore`
- Create: `manage.py`
- Create: `config/settings.py`
- Create: `config/urls.py`
- Create: `config/wsgi.py`
- Create: `catalog/apps.py`
- Create: `cart/apps.py`
- Create: `contact/apps.py`
- Create: `pages/apps.py`
- Create: `tests/test_settings.py`
- Test: `tests/test_settings.py`

**Interfaces:**
- Consumes: rien
- Produces: projet Django importable, `config.settings`, apps `catalog`, `cart`, `contact`, `pages`

- [ ] **Step 1: Write the failing test**

```python
def test_project_speaks_french_and_knows_the_contact_recipient():
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "fr-fr"
    assert settings.TIME_ZONE == "Europe/Paris"
    assert settings.CONTACT_RECIPIENT_EMAIL == "hellotoutous@hotmail.com"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_settings.py -v`

Expected: FAIL, Django settings are not configured.

- [ ] **Step 3: Write minimal implementation**

`pyproject.toml`

```toml
[project]
name = "hellotoutous"
version = "0.1.0"
description = "Hello Toutous storefront"
requires-python = ">=3.12"
dependencies = [
  "django>=5.2,<5.3",
]

[dependency-groups]
dev = [
  "pytest>=8.3",
  "pytest-django>=4.11",
  "ruff>=0.12",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`.gitignore`

```text
__pycache__/
*.py[cod]
.venv/
db.sqlite3
.pytest_cache/
```

Create the project and the four apps:

```powershell
uv python pin 3.12
uv sync
uv run django-admin startproject config .
uv run python manage.py startapp catalog
uv run python manage.py startapp cart
uv run python manage.py startapp contact
uv run python manage.py startapp pages
```

Replace `config/settings.py` with:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-hello-toutous")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
    "cart",
    "contact",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CONTACT_RECIPIENT_EMAIL = "hellotoutous@hotmail.com"
DEFAULT_FROM_EMAIL = "hellotoutous@hotmail.com"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

`config/urls.py`

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]
```

Create empty `pages/urls.py`:

```python
urlpatterns = []
```

Create `static/.gitkeep` and `templates/.gitkeep` so the static and template dirs exist.

Delete the default `tests.py` files created inside the apps. Tests live under `tests/`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_settings.py -v`

Expected: PASS

Run: `uv run ruff check .`

Expected: no findings.

- [ ] **Step 5: Commit**

```powershell
git add pyproject.toml uv.lock .python-version .gitignore manage.py config catalog cart contact pages static templates tests
git commit -m "feat: scaffold the Django project"
```

---

### Task 2: Design system et gabarit de page

**Files:**
- Create: `static/css/site.css`
- Create: `templates/base.html`
- Test: `tests/pages/test_base_template.py`

**Interfaces:**
- Consumes: `TEMPLATES["DIRS"]` et `STATICFILES_DIRS` de la tâche 1
- Produces: gabarit `base.html` avec les blocs `content`, lien d'évitement `#contenu`, feuille `site.css`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from django.template.loader import render_to_string


def test_base_template_exposes_tokens_fonts_and_skip_link():
    html = render_to_string("base.html", {"page_title": "Accueil"})

    assert "Fraunces" in html
    assert "Source Sans 3" in html
    assert "site.css" in html
    assert 'href="#contenu"' in html
    assert "Aller au contenu" in html

    css = Path("static/css/site.css").read_text(encoding="utf-8")
    for token in ("#D46A54", "#FEA674", "#FEBC97", "#6C4F3E", "#3F2A22", "#FFF6F0"):
        assert token in css
    assert "prefers-reduced-motion" in css
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/pages/test_base_template.py -v`

Expected: FAIL because the template does not exist.

- [ ] **Step 3: Write minimal implementation**

`templates/base.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ page_title|default:"Hello Toutous" }}{% endblock %} — Hello Toutous</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/site.css' %}">
</head>
<body>
  <a class="skip-link" href="#contenu">Aller au contenu</a>
  {% block header %}{% endblock %}
  <main id="contenu">
    {% block content %}{% endblock %}
  </main>
  {% block footer %}{% endblock %}
</body>
</html>
```

`static/css/site.css`

```css
:root {
  --color-accent: #D46A54;
  --color-bg-start: #FEA674;
  --color-bg-end: #FEBC97;
  --color-title: #6C4F3E;
  --color-text: #3F2A22;
  --color-navbar: #FFF6F0;
  --color-on-accent: #ffffff;
  --color-frame: #C4A574;
  --font-title: "Fraunces", Georgia, serif;
  --font-body: "Source Sans 3", "Segoe UI", sans-serif;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 1.125rem;
  line-height: 1.5;
  background: linear-gradient(to bottom, var(--color-bg-start), var(--color-bg-end));
}

h1, h2, h3 {
  font-family: var(--font-title);
  color: var(--color-title);
  font-weight: 560;
  line-height: 1.2;
}

a {
  color: inherit;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 3px solid var(--color-title);
  outline-offset: 2px;
}

.skip-link {
  position: absolute;
  left: 1rem;
  top: -4rem;
  background: var(--color-navbar);
  color: var(--color-title);
  padding: 0.5rem 1rem;
}

.skip-link:focus {
  top: 0.5rem;
  z-index: 20;
}

.button {
  display: inline-block;
  background: var(--color-accent);
  color: var(--color-on-accent);
  font-family: var(--font-body);
  font-weight: 700;
  border: 0;
  border-radius: 999px;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
}

.button[aria-busy="true"] {
  opacity: 0.7;
  cursor: progress;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/pages/test_base_template.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add static/css/site.css templates/base.html tests/pages/test_base_template.py
git commit -m "feat: add the visual base of the site"
```

---

### Task 3: Panier en session

**Files:**
- Create: `cart/services/__init__.py`
- Create: `cart/services/session_cart.py`
- Create: `cart/context_processors.py`
- Modify: `config/settings.py`
- Test: `tests/cart/test_session_cart.py`

**Interfaces:**
- Consumes: rien
- Produces:

```python
class CartLine:
    variant_id: int
    quantity: int
    with_knot: bool

def get_lines(session) -> list[CartLine]: ...
def item_count(session) -> int: ...
def add_line(session, *, variant_id: int, quantity: int, with_knot: bool) -> None: ...
def cart_count(request) -> dict[str, int]: ...  # clé "cart_item_count"
```

- [ ] **Step 1: Write the failing test**

```python
import pytest

from cart.services.session_cart import CartLine, add_line, get_lines, item_count


class MemorySession(dict):
    modified = False


def test_add_line_merges_the_same_variant_and_option():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=1, with_knot=False)
    add_line(session, variant_id=3, quantity=2, with_knot=False)

    assert get_lines(session) == [CartLine(variant_id=3, quantity=3, with_knot=False)]
    assert item_count(session) == 3


def test_knot_option_does_not_add_another_line():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=2, with_knot=True)

    assert get_lines(session) == [CartLine(variant_id=3, quantity=2, with_knot=True)]
    assert item_count(session) == 2


def test_same_variant_with_and_without_knot_are_distinct_lines():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=1, with_knot=False)
    add_line(session, variant_id=3, quantity=1, with_knot=True)

    assert item_count(session) == 2
    assert len(get_lines(session)) == 2


def test_quantity_below_one_is_rejected():
    session = MemorySession()
    with pytest.raises(ValueError):
        add_line(session, variant_id=3, quantity=0, with_knot=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cart/test_session_cart.py -v`

Expected: FAIL with `ModuleNotFoundError` or import error.

- [ ] **Step 3: Write minimal implementation**

`cart/services/session_cart.py`

```python
from dataclasses import dataclass

SESSION_KEY = "cart"


@dataclass(frozen=True)
class CartLine:
    variant_id: int
    quantity: int
    with_knot: bool


def get_lines(session) -> list[CartLine]:
    raw = session.get(SESSION_KEY, [])
    return [
        CartLine(
            variant_id=int(item["variant_id"]),
            quantity=int(item["quantity"]),
            with_knot=bool(item["with_knot"]),
        )
        for item in raw
    ]


def item_count(session) -> int:
    return sum(line.quantity for line in get_lines(session))


def add_line(session, *, variant_id: int, quantity: int, with_knot: bool) -> None:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")
    lines = get_lines(session)
    merged: list[CartLine] = []
    found = False
    for line in lines:
        if line.variant_id == variant_id and line.with_knot == with_knot:
            merged.append(
                CartLine(
                    variant_id=variant_id,
                    quantity=line.quantity + quantity,
                    with_knot=with_knot,
                )
            )
            found = True
        else:
            merged.append(line)
    if not found:
        merged.append(CartLine(variant_id=variant_id, quantity=quantity, with_knot=with_knot))
    session[SESSION_KEY] = [
        {
            "variant_id": line.variant_id,
            "quantity": line.quantity,
            "with_knot": line.with_knot,
        }
        for line in merged
    ]
    session.modified = True
```

`cart/context_processors.py`

```python
from cart.services.session_cart import item_count


def cart_count(request):
    return {"cart_item_count": item_count(request.session)}
```

Add `"cart.context_processors.cart_count"` to `TEMPLATES[...]["OPTIONS"]["context_processors"]` in `config/settings.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cart/test_session_cart.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add cart/services/session_cart.py cart/services/__init__.py cart/context_processors.py config/settings.py tests/cart/test_session_cart.py
git commit -m "feat: store the cart in the session"
```

---

### Task 4: Règles de prix et d'option nœud

**Files:**
- Create: `catalog/services/__init__.py`
- Create: `catalog/services/knot_rules.py`
- Create: `catalog/services/pricing.py`
- Test: `tests/catalog/test_knot_rules.py`
- Test: `tests/catalog/test_pricing.py`

**Interfaces:**
- Consumes: rien
- Produces:

```python
KNOT_CATEGORY_CODES = frozenset({"collar", "harness"})

class KnotOptionError(Exception):
    message: str

def validate_knot_option(*, category_code: str, offers_knot: bool, knot_price: Decimal | None) -> None: ...

class KnotNotOffered(Exception):
    pass

def unit_price(*, base_price: Decimal, offers_knot: bool, knot_price: Decimal | None, with_knot: bool) -> Decimal: ...
```

- [ ] **Step 1: Write the failing test**

`tests/catalog/test_knot_rules.py`

```python
from decimal import Decimal

import pytest

from catalog.services.knot_rules import KnotOptionError, validate_knot_option


def test_collar_can_offer_a_positive_knot_price():
    validate_knot_option(
        category_code="collar",
        offers_knot=True,
        knot_price=Decimal("8.50"),
    )


def test_harness_can_offer_a_knot():
    validate_knot_option(
        category_code="harness",
        offers_knot=True,
        knot_price=Decimal("1.00"),
    )


def test_other_categories_cannot_offer_a_knot():
    with pytest.raises(KnotOptionError) as exc:
        validate_knot_option(category_code="leash", offers_knot=True, knot_price=Decimal("5"))
    assert "colliers" in exc.value.message
    assert "harnais" in exc.value.message


@pytest.mark.parametrize("price", [None, Decimal("0"), Decimal("-1")])
def test_enabled_knot_requires_a_positive_price(price):
    with pytest.raises(KnotOptionError) as exc:
        validate_knot_option(category_code="collar", offers_knot=True, knot_price=price)
    assert "supérieur à 0" in exc.value.message


def test_disabled_knot_cannot_keep_a_price():
    with pytest.raises(KnotOptionError) as exc:
        validate_knot_option(
            category_code="collar",
            offers_knot=False,
            knot_price=Decimal("4"),
        )
    assert "vide" in exc.value.message


def test_disabled_knot_with_empty_price_is_valid():
    validate_knot_option(category_code="bow", offers_knot=False, knot_price=None)
```

`tests/catalog/test_pricing.py`

```python
from decimal import Decimal

import pytest

from catalog.services.pricing import KnotNotOffered, unit_price


def test_unit_price_without_knot_is_the_base_price():
    assert unit_price(
        base_price=Decimal("40.00"),
        offers_knot=True,
        knot_price=Decimal("8.00"),
        with_knot=False,
    ) == Decimal("40.00")


def test_unit_price_with_knot_adds_the_admin_supplement():
    assert unit_price(
        base_price=Decimal("40.00"),
        offers_knot=True,
        knot_price=Decimal("8.50"),
        with_knot=True,
    ) == Decimal("48.50")


def test_knot_price_is_refused_when_the_product_does_not_offer_it():
    with pytest.raises(KnotNotOffered):
        unit_price(
            base_price=Decimal("20.00"),
            offers_knot=False,
            knot_price=None,
            with_knot=True,
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/catalog/test_knot_rules.py tests/catalog/test_pricing.py -v`

Expected: FAIL on import.

- [ ] **Step 3: Write minimal implementation**

`catalog/services/knot_rules.py`

```python
from decimal import Decimal

KNOT_CATEGORY_CODES = frozenset({"collar", "harness"})


class KnotOptionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def validate_knot_option(*, category_code: str, offers_knot: bool, knot_price: Decimal | None) -> None:
    if not offers_knot:
        if knot_price is not None:
            raise KnotOptionError("Le supplément nœud doit rester vide quand l'option est désactivée.")
        return
    if category_code not in KNOT_CATEGORY_CODES:
        raise KnotOptionError("L'option avec nœud n'est disponible que pour les colliers et les harnais.")
    if knot_price is None or knot_price <= 0:
        raise KnotOptionError("Indiquez un supplément nœud supérieur à 0.")
```

`catalog/services/pricing.py`

```python
from decimal import Decimal


class KnotNotOffered(Exception):
    pass


def unit_price(*, base_price: Decimal, offers_knot: bool, knot_price: Decimal | None, with_knot: bool) -> Decimal:
    if not with_knot:
        return base_price
    if not offers_knot or knot_price is None or knot_price <= 0:
        raise KnotNotOffered("Knot option is not available for this product.")
    return base_price + knot_price
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/catalog/test_knot_rules.py tests/catalog/test_pricing.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add catalog/services tests/catalog/test_knot_rules.py tests/catalog/test_pricing.py
git commit -m "feat: price the knot option without adding a cart line"
```

---

### Task 5: Modèles du catalogue

**Files:**
- Modify: `catalog/models.py`
- Create: `catalog/selectors.py`
- Create: `catalog/migrations/0001_initial.py` (générée)
- Create: `catalog/migrations/0002_seed_references.py`
- Test: `tests/catalog/test_models.py`

**Interfaces:**
- Consumes: `validate_knot_option`
- Produces: modèles `Category`, `Size`, `Color`, `Product`, `ProductVariant`. `Product.clean()` reprend les règles nœud. `list_categories() -> list[Category]` trié par `position`.

Le champ `position` fixe l'ordre d'affichage. Il ne change ni les codes ni les libellés de la spec.

- [ ] **Step 1: Write the failing test**

```python
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from catalog.models import Category, Color, Product, ProductVariant, Size
from catalog.selectors import list_categories

pytestmark = pytest.mark.django_db


def test_reference_data_is_seeded_in_display_order():
    labels = [category.label for category in list_categories()]
    assert labels == [
        "Colliers",
        "Harnais",
        "Laisses",
        "Bandanas",
        "Distributeurs de sacs",
        "Sac à friandises",
        "Noeuds",
    ]
    assert list(Size.objects.order_by("position").values_list("code", flat=True)) == [
        "S",
        "M",
        "L",
        "XL",
    ]
    assert Color.objects.count() == 0


def test_product_accepts_several_sizes_and_colors():
    collar = Category.objects.get(code="collar")
    red = Color.objects.create(code="red", label="Rouge")
    blue = Color.objects.create(code="blue", label="Bleu")
    product = Product.objects.create(
        name="Collier floral",
        slug="collier-floral",
        category=collar,
        base_price=Decimal("42.00"),
        offers_knot=True,
        knot_price=Decimal("6.00"),
    )
    ProductVariant.objects.create(product=product, size=Size.objects.get(code="S"), color=red)
    ProductVariant.objects.create(product=product, size=Size.objects.get(code="M"), color=blue)

    assert product.variants.count() == 2


def test_duplicate_size_and_color_is_rejected():
    collar = Category.objects.get(code="collar")
    product = Product.objects.create(
        name="Collier lin",
        slug="collier-lin",
        category=collar,
        base_price=Decimal("30.00"),
    )
    size = Size.objects.get(code="M")
    ProductVariant.objects.create(product=product, size=size, color=None)
    with pytest.raises(IntegrityError):
        ProductVariant.objects.create(product=product, size=size, color=None)


def test_leash_cannot_offer_a_knot():
    product = Product(
        name="Laisse",
        slug="laisse",
        category=Category.objects.get(code="leash"),
        base_price=Decimal("25.00"),
        offers_knot=True,
        knot_price=Decimal("5.00"),
    )
    with pytest.raises(ValidationError):
        product.full_clean()


def test_collar_knot_price_is_required_when_the_option_is_on():
    product = Product(
        name="Collier",
        slug="collier",
        category=Category.objects.get(code="collar"),
        base_price=Decimal("25.00"),
        offers_knot=True,
        knot_price=None,
    )
    with pytest.raises(ValidationError):
        product.full_clean()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/catalog/test_models.py -v`

Expected: FAIL because the models are missing.

- [ ] **Step 3: Write minimal implementation**

`catalog/models.py`

```python
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from catalog.services.knot_rules import KnotOptionError, validate_knot_option


class Category(models.Model):
    code = models.SlugField(unique=True)
    label = models.CharField(max_length=80)
    position = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self) -> str:
        return self.label


class Size(models.Model):
    code = models.CharField(max_length=8, unique=True)
    label = models.CharField(max_length=8)
    position = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "taille"
        verbose_name_plural = "tailles"

    def __str__(self) -> str:
        return self.label


class Color(models.Model):
    code = models.SlugField(unique=True)
    label = models.CharField(max_length=80)

    class Meta:
        ordering = ["label"]
        verbose_name = "couleur"
        verbose_name_plural = "couleurs"

    def __str__(self) -> str:
        return self.label


class Product(models.Model):
    name = models.CharField("nom", max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField("description", blank=True)
    category = models.ForeignKey(Category, verbose_name="catégorie", on_delete=models.PROTECT)
    base_price = models.DecimalField(
        "prix de base",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    offers_knot = models.BooleanField("avec nœud", default=False)
    knot_price = models.DecimalField(
        "supplément nœud",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField("visible", default=True)

    class Meta:
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.category_id:
            return
        try:
            validate_knot_option(
                category_code=self.category.code,
                offers_knot=self.offers_knot,
                knot_price=self.knot_price,
            )
        except KnotOptionError as exc:
            raise ValidationError(exc.message) from exc


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, verbose_name="taille", on_delete=models.PROTECT)
    color = models.ForeignKey(
        Color,
        verbose_name="couleur",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "variante"
        verbose_name_plural = "variantes"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="uniq_variant_product_size_color",
                nulls_distinct=False,
            )
        ]

    def __str__(self) -> str:
        color = self.color.label if self.color_id else "sans couleur"
        return f"{self.product.name} — {self.size.label} — {color}"
```

`catalog/selectors.py`

```python
from catalog.models import Category


def list_categories() -> list[Category]:
    return list(Category.objects.order_by("position"))
```

Generate the schema migration, then add the seed migration:

```powershell
uv run python manage.py makemigrations catalog
```

`catalog/migrations/0002_seed_references.py`

```python
from django.db import migrations

CATEGORIES = [
    ("collar", "Colliers", 1),
    ("harness", "Harnais", 2),
    ("leash", "Laisses", 3),
    ("bandana", "Bandanas", 4),
    ("bag_dispenser", "Distributeurs de sacs", 5),
    ("treat_pouch", "Sac à friandises", 6),
    ("bow", "Noeuds", 7),
]
SIZES = [("S", "S", 1), ("M", "M", 2), ("L", "L", 3), ("XL", "XL", 4)]


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Size = apps.get_model("catalog", "Size")
    for code, label, position in CATEGORIES:
        Category.objects.create(code=code, label=label, position=position)
    for code, label, position in SIZES:
        Size.objects.create(code=code, label=label, position=position)


def unseed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Size = apps.get_model("catalog", "Size")
    Category.objects.filter(code__in=[code for code, _, _ in CATEGORIES]).delete()
    Size.objects.filter(code__in=[code for code, _, _ in SIZES]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
```

If `makemigrations` names the first file differently, point `dependencies` at that name.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/catalog/test_models.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add catalog/models.py catalog/selectors.py catalog/migrations tests/catalog/test_models.py
git commit -m "feat: store products with sizes, colors, and a knot supplement"
```

---

### Task 6: Ajout au panier

**Files:**
- Create: `catalog/services/add_to_cart.py`
- Test: `tests/catalog/test_add_to_cart.py`

**Interfaces:**
- Consumes: `add_line`, `get_lines`, `item_count`, `ProductVariant`, `KnotNotOffered`
- Produces:

```python
def add_variant_to_cart(session, *, variant: ProductVariant, quantity: int, with_knot: bool) -> None: ...
```

Une seule ligne est écrite. `with_knot=True` est refusé si l'article n'offre pas l'option. Le supplément n'est pas stocké dans la session : le prix se recalcule avec `unit_price` au moment de l'affichage, plus tard.

- [ ] **Step 1: Write the failing test**

```python
from decimal import Decimal

import pytest

from cart.services.session_cart import get_lines, item_count
from catalog.models import Category, Product, ProductVariant, Size
from catalog.services.add_to_cart import add_variant_to_cart
from catalog.services.pricing import KnotNotOffered, unit_price

pytestmark = pytest.mark.django_db


class MemorySession(dict):
    modified = False


def _variant(*, code: str, offers_knot: bool, knot_price: str | None) -> ProductVariant:
    product = Product.objects.create(
        name=code,
        slug=code,
        category=Category.objects.get(code=code),
        base_price=Decimal("40.00"),
        offers_knot=offers_knot,
        knot_price=Decimal(knot_price) if knot_price is not None else None,
    )
    product.full_clean()
    return ProductVariant.objects.create(product=product, size=Size.objects.get(code="M"), color=None)


def test_adding_with_knot_keeps_a_single_line_and_the_admin_price():
    session = MemorySession()
    variant = _variant(code="collar", offers_knot=True, knot_price="8.00")

    add_variant_to_cart(session, variant=variant, quantity=2, with_knot=True)

    assert get_lines(session)[0].with_knot is True
    assert item_count(session) == 2
    assert unit_price(
        base_price=variant.product.base_price,
        offers_knot=variant.product.offers_knot,
        knot_price=variant.product.knot_price,
        with_knot=True,
    ) == Decimal("48.00")


def test_leash_cannot_be_added_with_a_knot():
    session = MemorySession()
    variant = _variant(code="leash", offers_knot=False, knot_price=None)

    with pytest.raises(KnotNotOffered):
        add_variant_to_cart(session, variant=variant, quantity=1, with_knot=True)
    assert get_lines(session) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/catalog/test_add_to_cart.py -v`

Expected: FAIL on import.

- [ ] **Step 3: Write minimal implementation**

`catalog/services/add_to_cart.py`

```python
from cart.services.session_cart import add_line
from catalog.models import ProductVariant
from catalog.services.pricing import unit_price


def add_variant_to_cart(session, *, variant: ProductVariant, quantity: int, with_knot: bool) -> None:
    product = variant.product
    # Validate the option before touching the session. Price is not stored.
    unit_price(
        base_price=product.base_price,
        offers_knot=product.offers_knot,
        knot_price=product.knot_price,
        with_knot=with_knot,
    )
    add_line(session, variant_id=variant.id, quantity=quantity, with_knot=with_knot)
```

`unit_price` raises `KnotNotOffered` when the option is refused. This module does not catch it.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/catalog/test_add_to_cart.py -v`

Expected: PASS

Run: `uv run ruff check catalog/services/add_to_cart.py`

Expected: no findings.

- [ ] **Step 5: Commit**

```powershell
git add catalog/services/add_to_cart.py tests/catalog/test_add_to_cart.py
git commit -m "feat: add a variant to the cart without a second knot line"
```

---

### Task 7: Admin catalogue

**Files:**
- Modify: `catalog/admin.py`
- Modify: `config/urls.py` (l'admin est déjà branché en tâche 1, ne pas le dupliquer)
- Test: `tests/catalog/test_admin.py`

**Interfaces:**
- Consumes: `Product.clean`, `ProductVariant`
- Produces: admin « article » avec variantes en ligne, slug prérempli depuis le nom, messages français de `validate_knot_option`. Les messages de contact ne sont pas encore là.

- [ ] **Step 1: Write the failing test**

```python
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from catalog.models import Category, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password-long-123")
    client.force_login(user)
    return client


def _post_data(category_id: int, *, offers_knot: bool, knot_price: str) -> dict:
    data = {
        "name": "Collier test",
        "slug": "collier-test",
        "description": "",
        "category": str(category_id),
        "base_price": "42.00",
        "knot_price": knot_price,
        "is_active": "on",
        "variants-TOTAL_FORMS": "0",
        "variants-INITIAL_FORMS": "0",
        "variants-MIN_NUM_FORMS": "0",
        "variants-MAX_NUM_FORMS": "1000",
    }
    if offers_knot:
        data["offers_knot"] = "on"
    return data


def test_admin_rejects_a_knot_on_a_leash(admin_client):
    leash = Category.objects.get(code="leash")
    response = admin_client.post(
        "/admin/catalog/product/add/",
        _post_data(leash.id, offers_knot=True, knot_price="5.00"),
    )

    assert response.status_code == 200
    assert "colliers" in response.content.decode()
    assert Product.objects.count() == 0


def test_admin_saves_a_collar_knot_supplement(admin_client):
    collar = Category.objects.get(code="collar")
    response = admin_client.post(
        "/admin/catalog/product/add/",
        _post_data(collar.id, offers_knot=True, knot_price="6.50"),
    )

    assert response.status_code == 302
    product = Product.objects.get(slug="collier-test")
    assert product.knot_price == Decimal("6.50")
    assert product.offers_knot is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/catalog/test_admin.py -v`

Expected: FAIL with a 404 on the admin add page.

- [ ] **Step 3: Write minimal implementation**

`catalog/admin.py`

```python
from django.contrib import admin

from catalog.models import Category, Color, Product, ProductVariant, Size


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "offers_knot", "knot_price", "is_active")
    list_filter = ("category", "offers_knot", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline]


admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Color)
admin.site.site_header = "Hello Toutous"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/catalog/test_admin.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add catalog/admin.py tests/catalog/test_admin.py
git commit -m "feat: manage products and knot prices in the admin"
```

---

### Task 8: Navigation, pied de page et pages à venir

**Files:**
- Create: `templates/includes/navbar.html`
- Create: `templates/includes/footer.html`
- Create: `templates/pages/coming_soon.html`
- Modify: `templates/base.html`
- Modify: `static/css/site.css`
- Modify: `pages/views.py`
- Modify: `pages/urls.py`
- Test: `tests/pages/test_chrome.py`

**Interfaces:**
- Consumes: `cart_item_count`
- Produces: URLs `home` (pas encore de contenu final), `shop`, `category`, `product`, `size_guide`, `gallery`, `cart`

- [ ] **Step 1: Write the failing test**

```python
import pytest

from cart.services.session_cart import add_line

pytestmark = pytest.mark.django_db


def test_navbar_order_and_footer_are_on_every_placeholder(client):
    response = client.get("/galerie/")
    html = response.content.decode()

    assert response.status_code == 200
    boutique = html.index("Boutique")
    histoire = html.index("Notre histoire")
    tailles = html.index("Guide des tailles")
    galerie = html.index("Galerie")
    contact = html.index("Contact")
    assert boutique < histoire < tailles < galerie < contact
    assert 'href="/#notre-histoire"' in html
    assert 'href="/#contact"' in html
    assert 'href="/boutique/"' in html
    assert 'href="/guide-des-tailles/"' in html
    assert 'href="/galerie/"' in html
    assert 'href="/panier/"' in html
    assert "Panier (0)" in html
    assert "06 46 56 54 20" in html
    assert "tel:+33646565420" in html
    assert "hellotoutous@hotmail.com" in html
    assert "© Company 2026" in html
    assert "Cette page arrive dans une prochaine itération." in html
    assert 'href="mailto:hellotoutous@hotmail.com"' in html


def test_cart_count_follows_the_session(client):
    session = client.session
    add_line(session, variant_id=9, quantity=2, with_knot=False)
    session.save()

    response = client.get("/panier/")

    assert "Panier (2)" in response.content.decode()
    assert "Cette page arrive dans une prochaine itération." in response.content.decode()


@pytest.mark.parametrize(
    "path",
    [
        "/boutique/",
        "/boutique/collar/",
        "/boutique/collar/collier-floral/",
        "/guide-des-tailles/",
        "/galerie/",
        "/panier/",
    ],
)
def test_future_pages_answer(client, path):
    assert client.get(path).status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/pages/test_chrome.py -v`

Expected: FAIL with 404.

- [ ] **Step 3: Write minimal implementation**

`pages/views.py`

```python
from django.shortcuts import render


def coming_soon(request, page_title: str):
    return render(
        request,
        "pages/coming_soon.html",
        {"page_title": page_title},
    )
```

`pages/urls.py`

```python
from django.urls import path

from pages.views import coming_soon

urlpatterns = [
    path("", coming_soon, {"page_title": "Accueil"}, name="home"),
    path("boutique/", coming_soon, {"page_title": "Boutique"}, name="shop"),
    path(
        "boutique/<slug:category_code>/",
        coming_soon,
        {"page_title": "Boutique"},
        name="category",
    ),
    path(
        "boutique/<slug:category_code>/<slug:product_slug>/",
        coming_soon,
        {"page_title": "Article"},
        name="product",
    ),
    path("guide-des-tailles/", coming_soon, {"page_title": "Guide des tailles"}, name="size_guide"),
    path("galerie/", coming_soon, {"page_title": "Galerie"}, name="gallery"),
    path("panier/", coming_soon, {"page_title": "Panier"}, name="cart"),
]
```

The home route is replaced in task 9. Keep the name `home`.

`templates/includes/navbar.html`

```html
<header class="navbar">
  <nav class="navbar__links" aria-label="Navigation principale">
    <a href="{% url 'shop' %}">Boutique</a>
    <a href="{% url 'home' %}#notre-histoire">Notre histoire</a>
    <a href="{% url 'size_guide' %}">Guide des tailles</a>
    <a href="{% url 'gallery' %}">Galerie</a>
    <a href="{% url 'home' %}#contact">Contact</a>
  </nav>
  <a class="navbar__cart" href="{% url 'cart' %}" aria-live="polite">
    Panier ({{ cart_item_count }})
  </a>
</header>
```

`templates/includes/footer.html`

```html
<footer class="footer">
  <h2>Me contacter</h2>
  <p><a href="tel:+33646565420">06 46 56 54 20</a></p>
  <p><a href="mailto:hellotoutous@hotmail.com">hellotoutous@hotmail.com</a></p>
  <p>© Company 2026</p>
</footer>
```

`templates/pages/coming_soon.html`

```html
{% extends "base.html" %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
  <article class="coming-soon">
    <h1>{{ page_title }}</h1>
    <p>Cette page arrive dans une prochaine itération.</p>
    <p><a href="{% url 'home' %}">Retour à l'accueil</a></p>
  </article>
{% endblock %}
```

In `templates/base.html`, replace the empty header and footer blocks with the includes, outside the overridable blocks, so every page shows them:

```html
  {% include "includes/navbar.html" %}
  <main id="contenu">
    {% block content %}{% endblock %}
  </main>
  {% include "includes/footer.html" %}
```

Remove `{% block header %}` and `{% block footer %}`.

Append to `static/css/site.css`:

```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: var(--color-navbar);
  padding: 0.75rem 1.5rem;
}

.navbar__links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.navbar__links a {
  color: var(--color-title);
  text-decoration: none;
  font-weight: 600;
}

.navbar__cart {
  margin-left: auto;
  color: var(--color-accent);
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

body {
  padding-top: 4.5rem;
}

.footer {
  padding: 2rem 1.5rem 3rem;
}

.coming-soon {
  padding: 2rem 1.5rem 4rem;
}
```

The existing `body` rule in task 2 must gain `padding-top: 4.5rem` instead of a second `body` block. Edit the existing rule.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/pages/test_chrome.py tests/pages/test_base_template.py -v`

Expected: PASS. If the base test looks for the skip link, it still passes. The header include does not remove it.

- [ ] **Step 5: Commit**

```powershell
git add pages templates static/css/site.css tests/pages/test_chrome.py
git commit -m "feat: add the fixed navigation and coming-soon pages"
```

---

### Task 9: Page d'accueil

**Files:**
- Modify: `pages/views.py`
- Modify: `pages/urls.py`
- Create: `templates/pages/home.html`
- Modify: `static/css/site.css`
- Create: `static/js/carousel.js`
- Test: `tests/pages/test_home.py`

**Interfaces:**
- Consumes: `list_categories`, gabarit `base.html`
- Produces: vue `home`, template des sections 1 à 5 sans formulaire fonctionnel. La section contact affiche le texte et le titre du formulaire. Le formulaire branché arrive en tâche 10.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db


def test_home_renders_the_five_sections_in_order(client):
    html = client.get("/").content.decode()

    markers = [
        "HELLO TOUTOUS",
        "BOUTIQUE D'ACCESSOIRES POUR CHIENS",
        "Délais de fabrication 2 à 4 semaines",
        "Livraison offerte à partir de 150€ d'achat",
        "entièrement confectionnés à la main",
        "n'attendent que vous",
        "Colliers",
        "Noeuds",
        "Livraison dans le monde",
        "Qualité &amp; originalité",
        "QUI SE CACHE DERRIERE HELLO TOUTOUS ?",
        "C’est moi, Blandine",
        "atelier parisien",
        "A votre écoute",
        "sur Instagram",
        "Envie d'un accessoire sur-mesure ? Contacte-moi !",
    ]
    positions = [html.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert 'id="notre-histoire"' in html
    assert 'id="contact"' in html
    assert 'href="/boutique/collar/"' in html
    assert 'href="/boutique/bow/"' in html
    assert "instagram.com" not in html.lower()
    assert 'data-carousel' in html
    assert 'data-carousel-prev' in html
    assert 'data-carousel-next' in html
    assert "Photo précédente" in html
    assert "Photo suivante" in html


def test_motion_can_be_reduced():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    js = Path("static/js/carousel.js").read_text(encoding="utf-8")

    assert "marquee__track" in css
    assert "prefers-reduced-motion" in css
    assert "mouseenter" in js
    assert "focusin" in js
    assert "prefers-reduced-motion" in js
```

Copy the Blandine sentence from the spec if the apostrophe in `C’est` does not match the template. The test and the template must use the same characters as `docs/superpowers/specs/2026-10-06-hello-toutous-design.md`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/pages/test_home.py -v`

Expected: FAIL. `/` still renders the coming-soon page.

- [ ] **Step 3: Write minimal implementation**

`pages/views.py` — add `home` and keep `coming_soon`:

```python
from django.shortcuts import render

from catalog.selectors import list_categories


def home(request):
    return render(
        request,
        "pages/home.html",
        {"page_title": "Accueil", "categories": list_categories()},
    )


def coming_soon(request, page_title: str):
    return render(request, "pages/coming_soon.html", {"page_title": page_title})
```

In `pages/urls.py`, replace the home path:

```python
from pages.views import coming_soon, home

path("", home, name="home"),
```

`templates/pages/home.html`

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Accueil{% endblock %}

{% block content %}
  <section class="hero" aria-label="Hello Toutous">
    <div class="hero__photo">
      <div class="hero__card">
        <p class="hero__paw" aria-hidden="true">&#128062;</p>
        <p class="hero__name">HELLO TOUTOUS</p>
        <p class="hero__tag">BOUTIQUE D'ACCESSOIRES POUR CHIENS</p>
      </div>
    </div>
    <div class="marquee">
      <div class="marquee__track">
        <span>Délais de fabrication 2 à 4 semaines</span>
        <span>Livraison offerte à partir de 150€ d'achat</span>
        <span aria-hidden="true">Délais de fabrication 2 à 4 semaines</span>
        <span aria-hidden="true">Livraison offerte à partir de 150€ d'achat</span>
      </div>
    </div>
  </section>

  <section class="split">
    <div>
      <p>HELLO TOUTOUS vous propose des accessoires canins entièrement confectionnés à la main prêts à vous accompagner dans toutes vos aventures. Optez pour le style et le savoir-faire français.</p>
      <p>Nos colliers, laisses, harnais et autres accessoires n'attendent que vous !</p>
    </div>
    <div class="carousel" data-carousel>
      <button type="button" class="button" data-carousel-prev>Photo précédente</button>
      <div class="carousel__slides">
        <p data-slide>Photo à venir 1</p>
        <p data-slide hidden>Photo à venir 2</p>
        <p data-slide hidden>Photo à venir 3</p>
      </div>
      <button type="button" class="button" data-carousel-next>Photo suivante</button>
    </div>
  </section>

  <section class="categories" aria-labelledby="accessoires-titre">
    <h2 id="accessoires-titre">Accessoires</h2>
    <ul>
      {% for category in categories %}
        <li><a href="{% url 'category' category_code=category.code %}">{{ category.label }}</a></li>
      {% endfor %}
    </ul>
    <div class="split">
      <div>
        <h3>Livraison dans le monde</h3>
        <p>HELLO TOUTOUS vous livre dans le monde entier. Les délais de confection sont actuellement de 2 à 4 semaines. La livraison est offerte dès 150€ d'achat en France métropolitaine !</p>
      </div>
      <div>
        <h3>Qualité &amp; originalité</h3>
        <p>Les créations HELLO TOUTOUS sont exclusives. J'apporte un soin particulier aux finitions. Chaque modèle est unique et créé uniquement pour vous, à votre demande.</p>
      </div>
    </div>
  </section>

  <section class="split" id="notre-histoire">
    <div>
      <h2>QUI SE CACHE DERRIERE HELLO TOUTOUS ?</h2>
      <p>C’est moi, Blandine</p>
      <p>Passionnée de couture et ancienne maroquinière,</p>
      <p>j’ai créé HELLO TOUTOUS avec l’envie de mettre mon savoir-faire au service de nos compagnons à quatre pattes.</p>
      <p>Chaque accessoire est imaginé, confectionné et personnalisé à la main dans mon atelier parisien.</p>
    </div>
    <p class="placeholder">Photo de Blandine dans son atelier, à venir</p>
  </section>

  <section id="contact">
    <h2>A votre écoute</h2>
    <p>J'accorde beaucoup d'importance à votre confort et à votre tranquillité. N'hésitez pas à me contacter si vous avez la moindre question et je vous répondrai rapidement par mail, telephone ainsi que sur Instagram.</p>
    <h3>Envie d'un accessoire sur-mesure ? Contacte-moi !</h3>
  </section>
  <script src="{% static 'js/carousel.js' %}"></script>
{% endblock %}
```

`static/js/carousel.js`

```javascript
(function () {
  var root = document.querySelector("[data-carousel]");
  if (!root) {
    return;
  }
  var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var index = 0;
  var timer = null;

  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach(function (slide, slideIndex) {
      slide.hidden = slideIndex !== index;
    });
  }

  function stop() {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  function play() {
    if (reduce) {
      return;
    }
    stop();
    timer = window.setInterval(function () {
      show(index + 1);
    }, 4000);
  }

  root.addEventListener("mouseenter", stop);
  root.addEventListener("mouseleave", play);
  root.addEventListener("focusin", stop);
  root.addEventListener("focusout", play);
  root.querySelector("[data-carousel-prev]").addEventListener("click", function () {
    show(index - 1);
  });
  root.querySelector("[data-carousel-next]").addEventListener("click", function () {
    show(index + 1);
  });
  show(0);
  play();
})();
```

Append to `static/css/site.css`:

```css
.hero__photo {
  min-height: 28rem;
  display: grid;
  place-items: center;
  border: 1px solid var(--color-frame);
  background:
    linear-gradient(to bottom, rgb(254 166 116 / 35%), rgb(254 166 116 / 35%)),
    #e7c3a4;
}

.hero__card {
  background: rgb(255 246 240 / 88%);
  color: var(--color-title);
  text-align: center;
  padding: 1.5rem 2rem;
}

.hero__name {
  font-family: var(--font-title);
  font-size: 2.5rem;
  margin: 0;
}

.marquee {
  overflow: hidden;
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.marquee__track {
  display: flex;
  gap: 3rem;
  width: max-content;
  padding: 0.6rem 0;
  animation: marquee 18s linear infinite;
}

@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2.5rem 1.5rem;
}

.categories {
  padding: 1rem 1.5rem 2rem;
}

.placeholder {
  min-height: 16rem;
  display: grid;
  place-items: center;
  background: rgb(255 246 240 / 70%);
}

@media (max-width: 800px) {
  .split {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .marquee__track {
    animation: none;
    flex-wrap: wrap;
    width: auto;
    padding-left: 1rem;
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/pages/test_home.py tests/pages/test_chrome.py -v`

Expected: PASS

- [ ] **Step 5: Check the page in the browser**

Run: `uv run python manage.py migrate` then `uv run python manage.py runserver`

Open `http://127.0.0.1:8000/` at about 1280 px and about 390 px.

Confirm: navbar fixed while scrolling, menu order, both marquee sentences moving right to left, marquee still readable with reduced motion, carousel arrows change the visible placeholder, hover stops the carousel, sections stack on the narrow viewport, footer phone and e-mail.

- [ ] **Step 6: Commit**

```powershell
git add pages/views.py pages/urls.py templates/pages/home.html static/css/site.css static/js/carousel.js tests/pages/test_home.py
git commit -m "feat: publish the home page"
```

---

### Task 10: Formulaire de contact

**Files:**
- Create: `contact/models.py`
- Create: `contact/forms.py`
- Create: `contact/copy.py`
- Create: `contact/services/form_token.py`
- Create: `contact/services/submit_contact.py`
- Create: `contact/views.py`
- Create: `contact/admin.py`
- Modify: `contact/migrations/` (générée)
- Create: `pages/selectors.py`
- Modify: `config/urls.py`
- Modify: `pages/views.py`
- Modify: `templates/pages/home.html`
- Modify: `static/css/site.css`
- Test: `tests/contact/test_submit_contact.py`
- Test: `tests/contact/test_contact_view.py`

**Interfaces:**
- Consumes: `home` template section `#contact`, `CONTACT_RECIPIENT_EMAIL`
- Produces:

```python
SUCCESS = "Votre message a bien été envoyé."
EMAIL_FAILED = "L'envoi a échoué. Réessayez dans un instant."

class ContactPayload:
    name: str
    email: str
    city: str
    category: str
    category_label: str
    message: str

def issue_token(session) -> str: ...
def consume_token(session, posted: str) -> bool: ...

class ContactDeliveryError(Exception):
    pass

def submit_contact(payload: ContactPayload, *, recipient: str) -> ContactMessage: ...
```

`submit_contact` crée la ligne, envoie l'e-mail, et supprime la ligne si l'envoi lève une exception. La vue consomme le jeton seulement après une saisie valide. Un second POST avec le même jeton n'enregistre rien. Une saisie invalide ne consomme pas le jeton, réaffiche la page d'accueil, et montre l'erreur à côté du champ plus un résumé `role="alert"`. Le succès redirige vers `/#contact` et affiche `role="status"`.

- [ ] **Step 1: Write the failing test**

`tests/contact/test_submit_contact.py`

```python
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
```

`tests/contact/test_contact_view.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/contact -v`

Expected: FAIL on import or 404 on `/contact/`.

- [ ] **Step 3: Write minimal implementation**

`contact/copy.py`

```python
SUCCESS = "Votre message a bien été envoyé."
EMAIL_FAILED = "L'envoi a échoué. Réessayez dans un instant."
REQUIRED = "Ce champ est obligatoire."
INVALID_EMAIL = "Saisissez une adresse courriel valide."
```

`contact/models.py`

```python
from django.db import models


class MessageCategory(models.TextChoices):
    CUSTOM_ORDER = "custom_order", "Demande sur mesure"
    CUSTOMER_REVIEW = "customer_review", "Avis client"
    OTHER = "other", "Autre"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    city = models.CharField(max_length=120)
    category = models.CharField(max_length=32, choices=MessageCategory.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"
```

`contact/forms.py`

```python
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
```

`contact/services/form_token.py`

```python
import secrets

TOKEN_KEY = "contact_form_token"


def issue_token(session) -> str:
    token = secrets.token_urlsafe(16)
    session[TOKEN_KEY] = token
    session.modified = True
    return token


def current_token(session) -> str:
    token = session.get(TOKEN_KEY)
    if token:
        return token
    return issue_token(session)


def consume_token(session, posted: str) -> bool:
    expected = session.get(TOKEN_KEY)
    if not posted or posted != expected:
        return False
    session.pop(TOKEN_KEY, None)
    session.modified = True
    return True
```

`contact/services/submit_contact.py`

```python
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
```

`pages/selectors.py` builds the home page context. `contact/views.py` only decides what to answer.

`pages/selectors.py`

```python
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
```

`contact/views.py`

```python
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
```

`pages/views.py` complet :

```python
from django.shortcuts import render

from contact.forms import ContactForm
from pages.selectors import home_context


def home(request):
    return render(request, "pages/home.html", home_context(request, ContactForm()))


def coming_soon(request, page_title: str):
    return render(request, "pages/coming_soon.html", {"page_title": page_title})
```

`contact/admin.py`

```python
from django.contrib import admin

from contact.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "category")
    readonly_fields = ("name", "email", "city", "category", "message", "created_at")

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
```

`config/urls.py`

```python
from django.contrib import admin
from django.urls import include, path

from contact.views import submit_contact_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contact/", submit_contact_view, name="contact_submit"),
    path("", include("pages.urls")),
]
```

In `templates/pages/home.html`, under the form title:

```html
    {% if contact_success %}
      <p role="status">Votre message a bien été envoyé.</p>
    {% endif %}
    <form method="post" action="{% url 'contact_submit' %}" novalidate>
      {% csrf_token %}
      <input type="hidden" name="form_token" value="{{ contact_token }}">
      {% if form.non_field_errors %}
        <div role="alert">
          {% for error in form.non_field_errors %}<p>{{ error }}</p>{% endfor %}
        </div>
      {% endif %}
      <label for="{{ form.name.id_for_label }}">Nom</label>
      <input id="{{ form.name.id_for_label }}" name="{{ form.name.html_name }}" type="text" autocomplete="name" value="{{ form.name.value|default:'' }}" {% if form.name.errors %}aria-invalid="true" aria-describedby="error-name" autofocus{% endif %}>
      {% if form.name.errors %}<p id="error-name" role="alert">{{ form.name.errors.0 }}</p>{% endif %}

      <label for="{{ form.email.id_for_label }}">Courriel</label>
      <input id="{{ form.email.id_for_label }}" name="{{ form.email.html_name }}" type="email" autocomplete="email" value="{{ form.email.value|default:'' }}" {% if form.email.errors %}aria-invalid="true" aria-describedby="error-email" autofocus{% endif %}>
      {% if form.email.errors %}<p id="error-email" role="alert">{{ form.email.errors.0 }}</p>{% endif %}

      <label for="{{ form.city.id_for_label }}">Ville</label>
      <input id="{{ form.city.id_for_label }}" name="{{ form.city.html_name }}" type="text" autocomplete="address-level2" value="{{ form.city.value|default:'' }}" {% if form.city.errors %}aria-invalid="true" aria-describedby="error-city" autofocus{% endif %}>
      {% if form.city.errors %}<p id="error-city" role="alert">{{ form.city.errors.0 }}</p>{% endif %}

      <label for="{{ form.category.id_for_label }}">Catégorie du message</label>
      <select id="{{ form.category.id_for_label }}" name="{{ form.category.html_name }}" {% if form.category.errors %}aria-invalid="true" aria-describedby="error-category" autofocus{% endif %}>
        {% for value, label in form.category.field.choices %}
          <option value="{{ value }}" {% if form.category.value == value %}selected{% endif %}>{{ label }}</option>
        {% endfor %}
      </select>
      {% if form.category.errors %}<p id="error-category" role="alert">{{ form.category.errors.0 }}</p>{% endif %}

      <label for="{{ form.message.id_for_label }}">Message</label>
      <textarea id="{{ form.message.id_for_label }}" name="{{ form.message.html_name }}" rows="6" {% if form.message.errors %}aria-invalid="true" aria-describedby="error-message" autofocus{% endif %}>{{ form.message.value|default:'' }}</textarea>
      {% if form.message.errors %}<p id="error-message" role="alert">{{ form.message.errors.0 }}</p>{% endif %}

      <button class="button" type="submit">Envoyer</button>
    </form>
```

Le navigateur place le focus sur le premier `autofocus` du document, donc sur le premier champ invalide.

Append to `static/css/site.css`:

```css
.field-error,
[role="alert"] {
  color: #6f2218;
  font-weight: 700;
}

[role="status"] {
  background: var(--color-navbar);
  color: var(--color-title);
  padding: 0.75rem 1rem;
}
```

`#6F2218` is reserved for the error text, darker than the accent, so the error stays readable on the peach background.

`tests/conftest.py` sends e-mails to memory during tests:

```python
import pytest


@pytest.fixture(autouse=True)
def email_backend(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
```

Generate the contact migration:

```powershell
uv run python manage.py makemigrations contact
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/contact tests/pages/test_home.py -v`

Expected: PASS

The home test must still find the form title. The success paragraph is absent on a normal GET.

- [ ] **Step 5: Check the form in the browser**

With the server running, submit an empty form, then a bad e-mail, then a valid message.

Confirm: errors appear next to the fields and in a visible alert, the valid submit replaces the form state with « Votre message a bien été envoyé. », refresh does not show a second success created by a new POST, and the console backend (or the mailbox used in dev) receives one message to `hellotoutous@hotmail.com`.

- [ ] **Step 6: Commit**

```powershell
git add contact pages/views.py pages/selectors.py templates/pages/home.html static/css/site.css config/urls.py tests/contact tests/conftest.py
git commit -m "feat: send contact messages once and explain form errors"
```

---

## Couverture de la spec

| Besoin | Tâche |
| --- | --- |
| Couleurs, dégradé, polices, contraste du texte | 2, 9 |
| Navbar fixe, ordre du menu, Galerie, panier à droite | 8 |
| Compteur synchronisé avec la session | 3, 8 |
| « Avec nœud » change le prix sans ajouter de ligne | 3, 4, 6 |
| Option limitée aux colliers et harnais, prix admin | 4, 5, 7 |
| Hero, bandeau droite-gauche, reduced motion | 9 |
| Texte d'accroche et carrousel (pause au survol, flèches) | 9 |
| Catégories et deux textes côte à côte | 9 |
| Notre histoire et contact en ancres | 8, 9 |
| Formulaire, erreurs, succès, pas de double envoi | 10 |
| E-mail vers hellotoutous@hotmail.com | 10 |
| Pied de page | 8 |
| Pages à venir | 8 |
| Modèle en anglais, libellés français | 5, 7, 10 |
| Instagram sans lien | 9 |

Hors plan : Stripe, contenu du guide des tailles, contenu de la galerie, liste et fiche article, photos réelles, adresse Instagram.
