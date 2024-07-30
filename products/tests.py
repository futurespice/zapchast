import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Category, Product
from .factories import CategoryFactory, ProductFactory

@pytest.mark.django_db
class TestProductAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_product_list(self, api_client):
        ProductFactory.create_batch(3)
        url = reverse('product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_product_detail(self, api_client):
        product = ProductFactory()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name

    def test_product_create(self, api_client):
        category = CategoryFactory()
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '10.00',
            'category': category.pk
        }
        url = reverse('product-list')
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1
        assert Product.objects.get().name == 'New Product'

    def test_product_update(self, api_client):
        product = ProductFactory()
        data = {'name': 'Updated Product'}
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Product.objects.get(pk=product.pk).name == 'Updated Product'

    def test_product_delete(self, api_client):
        product = ProductFactory()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0