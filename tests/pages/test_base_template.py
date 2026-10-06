from pathlib import Path

from django.template.loader import render_to_string


def test_base_template_exposes_tokens_fonts_and_skip_link():
    html = render_to_string("base.html", {"page_title": "Accueil"})

    assert "Fraunces" in html
    assert "Source+Sans+3" in html
    assert "site.css" in html
    assert 'href="#contenu"' in html
    assert "Aller au contenu" in html

    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "Source Sans 3" in css
    for token in ("#D46A54", "#FEA674", "#FEBC97", "#6C4F3E", "#3F2A22", "#FFF6F0"):
        assert token in css
    assert "prefers-reduced-motion" in css
