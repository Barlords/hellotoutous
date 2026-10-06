from django.db import migrations

CATEGORIES = [
    ("collar", "Colliers", 1),
    ("harness", "Harnais", 2),
    ("leash", "Laisses", 3),
    ("bandana", "Bandanas", 4),
    ("bag_dispenser", "Distributeurs de sacs", 5),
    ("treat_pouch", "Sac à friandises", 6),
    ("bow", "Noeuds", 7),
]
SIZES = [("S", "S", 1), ("M", "M", 2), ("L", "L", 3), ("XL", "XL", 4)]


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Size = apps.get_model("catalog", "Size")
    for code, label, position in CATEGORIES:
        Category.objects.create(code=code, label=label, position=position)
    for code, label, position in SIZES:
        Size.objects.create(code=code, label=label, position=position)


def unseed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Size = apps.get_model("catalog", "Size")
    Category.objects.filter(code__in=[code for code, _, _ in CATEGORIES]).delete()
    Size.objects.filter(code__in=[code for code, _, _ in SIZES]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
