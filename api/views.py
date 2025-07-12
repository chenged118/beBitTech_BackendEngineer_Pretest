from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order

ACCEPTED_TOKEN = ('omni_pretest_token')


@api_view(['POST'])
def import_order(request):
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
def list_orders(request):
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
def update_order(request, order_id):
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
def delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    order.delete()
    return Response({"message": "Order deleted successfully."})