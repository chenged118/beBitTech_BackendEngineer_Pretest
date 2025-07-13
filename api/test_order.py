from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order

class OrderTestCase(APITestCase):
    """Test case for Order API"""
    def setUp(self):
        self.client = APIClient()
        self.valid_token = 'omni_pretest_token'
        self.order_data = {
            "access_token": self.valid_token,
            "order_number": "ORD-TEST-001",
            "total_price": 99.99
        }

    def test_create_order(self):
        """Test creating a new order"""
        response = self.client.post('/api/orders/', self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().order_number, "ORD-TEST-001")

    def test_list_orders(self):
        """Test listing orders"""
        Order.objects.create(order_number="ORD-TEST-001", total_price=99.99)
        response = self.client.get('/api/orders/list/?access_token=omni_pretest_token', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_order(self):
        """Test updating an order"""
        order = Order.objects.create(order_number="ORD-TEST-001", total_price=99.99)
        update_data = {
            "access_token": self.valid_token,
            "order_number": "ORD-UPDATED",
            "total_price": 88.88
        }
        response = self.client.put(f'/api/orders/{order.id}/update/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.order_number, "ORD-UPDATED")
        self.assertEqual(float(order.total_price), 88.88)

    def test_delete_order(self):
        """Test deleting an order"""
        order = Order.objects.create(order_number="ORD-DELETE", total_price=77.77)
        delete_data = {
            "access_token": self.valid_token
        }
        response = self.client.delete(f'/api/orders/{order.id}/delete/', delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 0)
    
    def test_create_order_missing_fields(self):
        """Test missing required fields returns error response"""
        data = {
            "access_token": "omni_pretest_token",
            "order_number": ""
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_order_invalid_token(self):
        """Test using an invalid token results in access denied"""
        data = {
            "access_token": "wrong_token",
            "order_number": "ORD-00003",
            "total_price": 999.99
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Invalid access token.")

    def test_create_order_duplicate_number(self):
        """Test duplicated order_number"""
        Order.objects.create(order_number="ORD-00001", total_price=123.45)
        data = {
            "access_token": "omni_pretest_token",
            "order_number": "ORD-00001",  # duplicate
            "total_price": 888.88
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Order number already exists.")

    def test_get_single_order(self):
        """Test retrieving a single order by ID"""
        order = Order.objects.create(order_number="ORD-SINGLE", total_price=100.00)
        response = self.client.get(f'/api/orders/list/?id={order.id}&access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_number'], "ORD-SINGLE")

    def test_get_multiple_orders(self):
        """Test retrieving multiple orders by IDs"""
        order1 = Order.objects.create(order_number="ORD-MULTI-1", total_price=111.11)
        order2 = Order.objects.create(order_number="ORD-MULTI-2", total_price=222.22)
        response = self.client.get(f'/api/orders/list/?id={order1.id}&id={order2.id}&access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = {order["order_id"] for order in response.data}
        self.assertIn(order1.id, returned_ids)
        self.assertIn(order2.id, returned_ids)

    def test_get_nonexistent_order(self):
        """Test retrieving an order that does not exist"""
        response = self.client.get('/api/orders/list/?id=99999&access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_invalid_id_format(self):
        """Test passing invalid ID format (non-integer)"""
        response = self.client.get('/api/orders/list/?id=abc&access_token=omni_pretest_token')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_order_invalid_token(self):
        """Test updating an order with invalid token"""
        order = Order.objects.create(order_number="ORD-00010", total_price=1.0)
        data = {
            "access_token": "wrong_token",
            "total_price": 999.0
        }
        response = self.client.put(f'/api/orders/{order.id}/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_invalid_token(self):
        """Test deleting an order with invalid token"""
        order = Order.objects.create(order_number="ORD-00020", total_price=1.0)
        data = {
            "access_token": "wrong_token"
        }
        response = self.client.delete(f'/api/orders/{order.id}/delete/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)