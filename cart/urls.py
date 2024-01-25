from django.urls import path
from .views import add_to_cart,remove_from_cart,clear_cart,cart,checkout,place_order,order_complete,download_invoice,delete_order,apply_coupon,remove_coupon
urlpatterns = [
    path('add-to-cart/<int:id>/',add_to_cart,name='add_to_cart'),
    path('remove-from-cart/<int:id>/',remove_from_cart,name='remove_from_cart'),
    path('clear-cart/',clear_cart,name='clear_cart'),
    path('cart/',cart,name='cart'),
    path('checkout/',checkout,name='checkout'),
    path('place-order/',place_order,name='place_order'),
    path('order-complete',order_complete,name='order_complete'),
    path('download_invoice/<int:order_id>/', download_invoice, name='download_invoice'),    
    path('delete_order/<int:order_id>/', delete_order, name='delete_order'),
    path('coupon',apply_coupon,name='coupon'),
    path('remove_coupon/',remove_coupon,name='remove_coupon'),

]
