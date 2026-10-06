from catalog.models import Category


def list_categories() -> list[Category]:
    return list(Category.objects.order_by("position"))
