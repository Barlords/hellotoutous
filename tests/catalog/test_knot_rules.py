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
