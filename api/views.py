from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order

ACCEPTED_TOKEN = ('omni_pretest_token')


@api_view(['POST', 'GET'])
def import_order(request):
    if request.method == 'POST':
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

    elif request.method == 'GET':
        order_number = request.query_params.get('order_number')

        if order_number:
            # 查詢單一訂單
            try:
                order = Order.objects.get(order_number=order_number)
                return Response({
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "total_price": str(order.total_price),
                    "created_time": order.created_time
                })
            except Order.DoesNotExist:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 查詢所有訂單
            orders = Order.objects.all().order_by('-created_time')
            data = []
            for order in orders:
                data.append({
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "total_price": str(order.total_price),
                    "created_time": order.created_time
                })
            return Response(data)