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
