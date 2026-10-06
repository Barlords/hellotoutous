from django.shortcuts import render

from contact.forms import ContactForm
from pages.selectors import home_context


def home(request):
    return render(request, "pages/home.html", home_context(request, ContactForm()))


def coming_soon(request, page_title: str, **kwargs):
    return render(request, "pages/coming_soon.html", {"page_title": page_title})
