from django.db import migrations
from django.contrib.postgres.search import SearchVector

def update_search_vectors(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.update(search_vector=SearchVector('name', weight='A') + SearchVector('description', weight='B'))

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_subcategory_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(update_search_vectors),
    ]