from django.urls import path
from .views import add_to_cart,remove_from_cart,clear_cart,cart

urlpatterns = [
    path('add-to-cart/<int:id>/',add_to_cart,name='add_to_cart'),
    path('remove-from-cart/<int:id>/',remove_from_cart,name='remove_from_cart'),
    path('clear-cart/',clear_cart,name='clear_cart'),
    path('cart/',cart,name='cart'),
    
]
