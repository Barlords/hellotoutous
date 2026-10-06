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
