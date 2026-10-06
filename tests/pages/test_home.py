from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db


def test_home_renders_the_five_sections_in_order(client):
    html = client.get("/").content.decode()

    markers = [
        "img/brand_noborder.png",
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
        "Envie d'un accessoire sur-mesure ? Contactez-moi !",
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
