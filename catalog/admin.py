from django.contrib import admin

from catalog.models import Category, Color, Product, ProductVariant, Size


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "offers_knot", "knot_price", "is_active")
    list_filter = ("category", "offers_knot", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline]


admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Color)
admin.site.site_header = "Hello Toutous"
