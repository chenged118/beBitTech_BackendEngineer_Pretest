from .decorators import require_token
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .models import Product

load_dotenv()
ACCEPTED_TOKEN = os.getenv("ACCEPTED_TOKEN")


@api_view(['POST'])
@require_token
def import_order(request):
    """Import a new order."""
    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    order_number = request.data.get('order_number')
    total_price = request.data.get('total_price')

    if not order_number or total_price is None:
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    if Order.objects.filter(order_number=order_number).exists():
        return Response({"error": "Order number already exists."}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        order_number=order_number,
        total_price=total_price
    )

    return Response({
        "message": "Order imported successfully.",
        "order_id": order.id,
        "order_number": order.order_number
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@require_token
def list_orders(request):
    """
    Handle GET request to retrieve orders.
    - If ?id= provided (one or more), return matching orders.
    - If no id provided, return all orders.
    """
    access_token = request.query_params.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)
    
    ids = request.GET.getlist('id')  # ?id=1&id=2 支援多個
    if ids:
        try:
            ids = [int(i) for i in ids]
        except ValueError:
            return Response({"error": "Invalid ID format."}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(id__in=ids)
        if not orders.exists():
            return Response({"error": "No matching orders found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        orders = Order.objects.all()

    data = [
        {
            "order_id": order.id,
            "order_number": order.order_number,
            "total_price": float(order.total_price),
            "created_time": order.created_time
        }
        for order in orders
    ]
    return Response(data)


@api_view(['PUT'])
@require_token
def update_order(request, order_id):
    """Update an existing order by ID."""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    order.order_number = request.data.get('order_number', order.order_number)
    order.total_price = request.data.get('total_price', order.total_price)
    order.save()
    return Response({"message": "Order updated successfully."})


@api_view(['DELETE'])
@require_token
def delete_order(request, order_id):
    """Delete an existing order by ID."""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    order.delete()
    return Response({"message": "Order deleted successfully."})

@api_view(['POST'])
@require_token
def create_product(request):
    """Create a new product."""
    name = request.data.get('name')
    price = request.data.get('price')

    if not name or price is None:
        return Response({"error": "Missing product name or price."}, status=status.HTTP_400_BAD_REQUEST)

    product = Product.objects.create(name=name, price=price)

    return Response({
        "message": "Product created successfully.",
        "product_id": product.id,
        "name": product.name,
        "price": float(product.price)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@require_token
def list_products(request):
    """List all products."""
    products = Product.objects.all()
    data = [
        {
            "product_id": p.id,
            "name": p.name,
            "price": float(p.price),
            "created_time": p.created_time
        }
        for p in products
    ]
    return Response(data)


@api_view(['GET'])
@require_token
def get_product(request, product_id):
    """Retrieve a single product by ID."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    data = {
        "product_id": product.id,
        "name": product.name,
        "price": float(product.price),
        "created_time": product.created_time
    }
    return Response(data)


@api_view(['PUT'])
@require_token
def update_product(request, product_id):
    """Update an existing product by ID."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    name = request.data.get('name', product.name)
    price = request.data.get('price', product.price)

    product.name = name
    product.price = price
    product.save()

    return Response({"message": "Product updated successfully."})


@api_view(['DELETE'])
@require_token
def delete_product(request, product_id):
    """Delete an existing product by ID."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response({"message": "Product deleted successfully."})