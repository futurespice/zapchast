from rest_framework import serializers
from .models import Category, Subcategory, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):
        # Проверка характеристик в соответствии с подкатегорией
        subcategory = data.get('subcategory')
        characteristics = data.get('characteristics', {})

        # Здесь можно добавить логику проверки характеристик
        # в зависимости от подкатегории

        return data