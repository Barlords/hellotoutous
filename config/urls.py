from django.contrib import admin
from django.urls import include, path

from contact.views import submit_contact_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contact/", submit_contact_view, name="contact_submit"),
    path("", include("pages.urls")),
]
