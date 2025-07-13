from .decorators import require_token
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order

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