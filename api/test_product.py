from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product

class ProductTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_token = 'omni_pretest_token'
        self.product_data = {
            "access_token": self.valid_token,
            "name": "Test Product",
            "price": 99.99,
        }

    def test_create_product(self):
        """Test creating a new product"""
        response = self.client.post("/api/products/", self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_list_products(self):
        """Test listing all products"""
        Product.objects.create(name="New Product", price=49.99)
        response = self.client.get('/api/products/list/?access_token=omni_pretest_token', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_single_product(self):
        """Test retrieving a single product by ID"""
        product = Product.objects.create(name="New Product", price=49.99)
        response = self.client.get(f'/api/products/list/?id={product.id}&access_token=omni_pretest_token', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], product.name)

    def test_update_product(self):
        """Test updating a product"""
        product = Product.objects.create(name="New Product", price=49.99)
        update_data = {
            "access_token": self.valid_token,
            "name": "Updated Product",
            "price": 79.99,
        }
        response = self.client.put(f'/api/products/{product.id}/update/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, "Updated Product")

    def test_delete_product(self):
        """Test deleting a product"""
        delete_data = {
            "access_token": self.valid_token
        }
        product = Product.objects.create(name="New Product", price=49.99)
        response = self.client.delete(f'/api/products/{product.id}/delete/', delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 0)

    def test_create_product_missing_fields(self):
        """Test creating product with missing fields"""
        data = {
            "access_token": "omni_pretest_token",
            "name": "",
            "price": "",
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_token(self):
        """Test using an invalid token results in access denied"""
        data = {
            "access_token": "wrong_token",
            "name": "Updated Product",
            "price": 999.99
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Invalid access token.")

    def test_access_without_token(self):
        """Test accessing API without token"""
        response = self.client.get('/api/products/list/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_product(self):
        """Test retrieving a product that doesn't exist"""
        response = self.client.get('/api/products/99999/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)