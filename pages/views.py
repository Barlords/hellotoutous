from django.shortcuts import render


def coming_soon(request, page_title: str, **kwargs):
    return render(
        request,
        "pages/coming_soon.html",
        {"page_title": page_title},
    )
