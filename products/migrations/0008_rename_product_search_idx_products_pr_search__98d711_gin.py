# Generated by Django 5.0.7 on 2024-07-29 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20240729_1650'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='product',
            new_name='products_pr_search__98d711_gin',
            old_name='product_search_idx',
        ),
    ]
