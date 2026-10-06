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
