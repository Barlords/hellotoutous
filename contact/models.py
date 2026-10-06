from django.db import models


class MessageCategory(models.TextChoices):
    CUSTOM_ORDER = "custom_order", "Demande sur mesure"
    CUSTOMER_REVIEW = "customer_review", "Avis client"
    OTHER = "other", "Autre"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    city = models.CharField(max_length=120)
    category = models.CharField(max_length=32, choices=MessageCategory.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"
