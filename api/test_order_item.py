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

    def test_get_single_order_item(self):
        """Test retrieving a single OrderItem"""
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price_at_order=50.0)
        response = self.client.get(f"/api/order-items/list/?id={item.id}&access_token={self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], item.id)

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
        self.assertEqual(float(item.price_at_order), 45.0)

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

    def test_access_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/api/order-items/list/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)