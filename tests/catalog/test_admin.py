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
