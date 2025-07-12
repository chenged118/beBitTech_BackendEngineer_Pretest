from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order

ACCEPTED_TOKEN = ('omni_pretest_token')


@api_view(['POST'])
def import_order(request):
    # 驗證 access_token
    access_token = request.data.get('access_token')
    if access_token != ACCEPTED_TOKEN:
        return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)

    # 解析資料欄位
    order_number = request.data.get('order_number')
    total_price = request.data.get('total_price')

    if not order_number or total_price is None:
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    # 檢查是否已有相同訂單編號
    if Order.objects.filter(order_number=order_number).exists():
        return Response({"error": "Order number already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # 建立訂單
    order = Order.objects.create(
        order_number=order_number,
        total_price=total_price
    )

    return Response({
        "message": "Order imported successfully.",
        "order_id": order.id,
        "order_number": order.order_number
    }, status=status.HTTP_201_CREATED)