from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from products.models import Product, Category, Subcategory
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Creates default groups and permissions'

    def handle(self, *args, **options):
        # Создание групп
        client_group, _ = Group.objects.get_or_create(name='Клиент')
        seller_group, _ = Group.objects.get_or_create(name='Продавец')

        # Получение необходимых разрешений
        product_content_type = ContentType.objects.get_for_model(Product)
        category_content_type = ContentType.objects.get_for_model(Category)
        subcategory_content_type = ContentType.objects.get_for_model(Subcategory)

        view_product = Permission.objects.get(content_type=product_content_type, codename='view_product')
        add_product = Permission.objects.get(content_type=product_content_type, codename='add_product')
        change_product = Permission.objects.get(content_type=product_content_type, codename='change_product')
        delete_product = Permission.objects.get(content_type=product_content_type, codename='delete_product')

        view_category = Permission.objects.get(content_type=category_content_type, codename='view_category')
        view_subcategory = Permission.objects.get(content_type=subcategory_content_type, codename='view_subcategory')

        # Назначение разрешений для группы Клиент
        client_group.permissions.add(view_product, view_category, view_subcategory)

        # Назначение разрешений для группы Продавец
        seller_group.permissions.add(view_product, add_product, change_product, delete_product,
                                     view_category, view_subcategory)

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions'))