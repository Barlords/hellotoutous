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
