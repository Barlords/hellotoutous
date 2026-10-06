from django.shortcuts import render

from catalog.selectors import list_categories


def home(request):
    return render(
        request,
        "pages/home.html",
        {"page_title": "Accueil", "categories": list_categories()},
    )


def coming_soon(request, page_title: str, **kwargs):
    return render(
        request,
        "pages/coming_soon.html",
        {"page_title": page_title},
    )
