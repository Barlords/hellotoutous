from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from catalog.services.knot_rules import KnotOptionError, validate_knot_option


class Category(models.Model):
    code = models.SlugField(unique=True)
    label = models.CharField(max_length=80)
    position = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self) -> str:
        return self.label


class Size(models.Model):
    code = models.CharField(max_length=8, unique=True)
    label = models.CharField(max_length=8)
    position = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "taille"
        verbose_name_plural = "tailles"

    def __str__(self) -> str:
        return self.label


class Color(models.Model):
    code = models.SlugField(unique=True)
    label = models.CharField(max_length=80)

    class Meta:
        ordering = ["label"]
        verbose_name = "couleur"
        verbose_name_plural = "couleurs"

    def __str__(self) -> str:
        return self.label


class Product(models.Model):
    name = models.CharField("nom", max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField("description", blank=True)
    category = models.ForeignKey(Category, verbose_name="catégorie", on_delete=models.PROTECT)
    base_price = models.DecimalField(
        "prix de base",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    offers_knot = models.BooleanField("avec nœud", default=False)
    knot_price = models.DecimalField(
        "supplément nœud",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField("visible", default=True)

    class Meta:
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.category_id:
            return
        try:
            validate_knot_option(
                category_code=self.category.code,
                offers_knot=self.offers_knot,
                knot_price=self.knot_price,
            )
        except KnotOptionError as exc:
            raise ValidationError(exc.message) from exc


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, verbose_name="taille", on_delete=models.PROTECT)
    color = models.ForeignKey(
        Color,
        verbose_name="couleur",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "variante"
        verbose_name_plural = "variantes"
        constraints = [
            # SQLite 3.45 has no NULLS NOT DISTINCT, and Django skips
            # nulls_distinct=False on this backend. Partial unique indexes
            # enforce the same rule, including variants without a color.
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                condition=models.Q(color__isnull=False),
                name="uniq_variant_product_size_color",
            ),
            models.UniqueConstraint(
                fields=["product", "size"],
                condition=models.Q(color__isnull=True),
                name="uniq_variant_product_size_without_color",
            ),
        ]

    def __str__(self) -> str:
        color = self.color.label if self.color_id else "sans couleur"
        return f"{self.product.name} — {self.size.label} — {color}"
