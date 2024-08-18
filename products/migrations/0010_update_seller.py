# products/migrations/xxxx_set_default_seller.py

from django.db import migrations

def set_default_seller(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    CustomUser = apps.get_model('users', 'CustomUser')
    default_seller = CustomUser.objects.filter(user_type=2).first()  # Предполагаем, что 2 - это тип "продавец"
    if default_seller:
        Product.objects.filter(seller__isnull=True).update(seller=default_seller)

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_product_seller'),  # Замените на вашу предыдущую миграцию
    ]

    operations = [
        migrations.RunPython(set_default_seller),
    ]