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
