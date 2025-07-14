from .decorators import require_token
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .models import Product
from .models import OrderItem

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
    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

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
    """List products by ID or all products if no ID is provided."""
    access_token = request.query_params.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    ids = request.query_params.get('id')

    if ids:
        try:
            id_list = [int(i.strip()) for i in ids.split(',')]
        except ValueError:
            return Response({"error": "Invalid ID format."}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(id__in=id_list)
        if not products.exists():
            return Response({"error": "Product(s) not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        products = Product.objects.all()

    data = [
        {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
        }
        for product in products
    ]
    return Response(data)


@api_view(['PUT'])
@require_token
def update_product(request, product_id):
    """Update an existing product by ID."""
    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

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

@api_view(['POST'])
@require_token
def create_order_item(request):
    try:
        order_id = request.data.get('order_id')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not order_id or not product_id or quantity is None:
            return Response(
                {"error": "Missing required fields: order_id, product_id, quantity"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.get(id=order_id)
        product = Product.objects.get(id=product_id)
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_order=product.price
        )
        return Response({
            "id": item.id,
            "order_id": item.order.id,
            "product_id": item.product.id,
            "quantity": item.quantity,
            "price_at_order": float(item.price_at_order)
        }, status=status.HTTP_201_CREATED)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@require_token
def list_order_items(request):
    item_id = request.query_params.get('id')
    
    if item_id:
        try:
            item = OrderItem.objects.get(id=item_id)
            return Response({
                "id": item.id,
                "order_id": item.order.id,
                "product_id": item.product.id,
                "quantity": item.quantity,
                "price_at_order": float(item.price_at_order)
            })
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        items = OrderItem.objects.all()
        data = [
            {
                "id": item.id,
                "order_id": item.order.id,
                "product_id": item.product.id,
                "quantity": item.quantity,
                "price_at_order": float(item.price_at_order)
            } for item in items
        ]
        if not data:
            return Response({"message": "No order items found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)

@api_view(['PUT'])
@require_token
def update_order_item(request, item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
        quantity = request.data.get('quantity')
        if quantity:
            item.quantity = int(quantity)
        item.save()
        return Response({
            "id": item.id,
            "quantity": item.quantity,
            "price_at_order": float(item.price_at_order)
        })
    except OrderItem.DoesNotExist:
        return Response({"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@require_token
def delete_order_item(request, item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
        item.delete()
        return Response({"message": "Order item deleted."})
    except OrderItem.DoesNotExist:
        return Response({"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)