from django.contrib import admin
from django.urls import path
from api.views import list_orders, import_order, update_order, delete_order

urlpatterns = [
    path('import-order/', import_order, name='import_order'),
    path('import-order/list/', list_orders, name='list_orders'),
    path('import-order/<int:order_id>/update/', update_order, name='update_order'),
    path('import-order/<int:order_id>/delete/', delete_order, name='delete_order'),
]