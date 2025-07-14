from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order, Product, OrderItem

class OrderItemTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token = 'omni_pretest_token'
        self.order = Order.objects.create(order_number="ORD-001", total_price=0)
        self.product = Product.objects.create(name="Test Product", price=50.0)

    def test_create_order_item(self):
        """Test creating a new OrderItem"""
        data = {
            "access_token": self.token,
            "order_id": self.order.id,
            "product_id": self.product.id,
            "quantity": 2,
            "price_at_order": 50.0
        }
        response = self.client.post("/api/order-items/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_list_order_items(self):
        """Test listing all OrderItems"""
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        response = self.client.get(f"/api/order-items/list/?access_token={self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_order_item(self):
        """Test updating an OrderItem"""
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        data = {
            "access_token": self.token,
            "quantity": 3,
            "price_at_order": 45.0
        }
        response = self.client.put(f"/api/order-items/{item.id}/update/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(float(item.price_at_order), 50.0)

    def test_delete_order_item(self):
        """Test deleting an OrderItem"""
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        data = {"access_token": self.token}
        response = self.client.delete(f"/api/order-items/{item.id}/delete/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_create_order_item_missing_fields(self):
        """Test creating OrderItem with missing fields"""
        data = {
            "access_token": self.token,
            "order_id": self.order.id,
            # Missing product_id and quantity
        }
        response = self.client.post("/api/order-items/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_item_nonexistent_order(self):
        """Test creating OrderItem with nonexistent order"""
        data = {
            "access_token": self.token,
            "order_id": 99999,  # Nonexistent order ID
            "product_id": self.product.id,
            "quantity": 2,
            "price_at_order": 50.0
        }
        response = self.client.post("/api/order-items/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_item_nonexistent_product(self):
        """Test creating OrderItem with nonexistent product"""
        data = {
            "access_token": self.token,
            "order_id": self.order.id,
            "product_id": 99999,  # Nonexistent product ID
            "quantity": 2,
            "price_at_order": 50.0
        }
        response = self.client.post("/api/order-items/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_item_invalid_quantity_format(self):
        """Test creating OrderItem with invalid quantity format"""
        data = {
            "access_token": self.token,
            "order_id": self.order.id,
            "product_id": self.product.id,
            "quantity": "three",
        }
        response = self.client.post("/api/order-items/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_single_order_item(self):
        """Test retrieving a single OrderItem"""
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        response = self.client.get(f"/api/order-items/list/?id={item.id}&access_token={self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], item.id)

    def test_get_nonexistent_order_item(self):
        """Test retrieving an OrderItem that does not exist"""
        response = self.client.get('/api/order-items/list/?access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)

    def test_get_nonexistent_order_item_by_id(self):
        """Test retrieving an order item that does not exist"""
        response = self.client.get('/api/order-items/list/?id=99999&access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_update_nonexistent_order_item(self):
        """Test updating an order item that does not exist"""
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        data = {
            "access_token": "omni_pretest_token",
            "quantity": 3,
            "price_at_order": 45.0
        }
        response = self.client.put(f"/api/order-items/99999/update/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_delete_nonexistent_order_item(self):
        """Test deleting an order item that does not exist"""
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        data = {
            "access_token": "omni_pretest_token",
            "total_price": 999.0
        }
        response = self.client.delete(f'/api/order-items/99999/delete/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_order_item_subtotal(self):
        """Test that subtotal() returns correct value"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_order=25.50
        )
        expected_subtotal = 3 * 25.50
        self.assertEqual(item.subtotal(), expected_subtotal)