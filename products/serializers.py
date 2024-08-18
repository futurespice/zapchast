from rest_framework import serializers
from .models import Category, Subcategory, Product, ProductImage, Review, Favorite
from django.conf import settings

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'subcategory', 'seller', 'created_at', 'updated_at']
        read_only_fields = ['seller', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Если переводы названия не предоставлены, используем значение 'name'
        name = data.get('name', '')
        for lang_code, _ in settings.LANGUAGES:
            if f'name_{lang_code}' not in data:
                data[f'name_{lang_code}'] = name

        # Убираем ненужные поля описания
        for lang_code, _ in settings.LANGUAGES:
            data.pop(f'description_{lang_code}', None)

        return super().to_internal_value(data)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['seller'] = request.user
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['user']