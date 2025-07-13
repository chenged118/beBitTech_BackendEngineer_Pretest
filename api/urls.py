from django.contrib import admin
from django.urls import path
from api.views import list_orders, import_order, update_order, delete_order
from api.views import list_products, create_product, update_product, delete_product

urlpatterns = [
    path('orders/', import_order, name='import_order'),
    path('orders/list/', list_orders, name='list_orders'),
    path('orders/<int:order_id>/update/', update_order, name='update_order'),
    path('orders/<int:order_id>/delete/', delete_order, name='delete_order'),

    path('products/', create_product, name='create_product'),
    path('products/list/', list_products, name='list_products'),
    path('products/<int:product_id>/update/', update_product, name='update_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
]