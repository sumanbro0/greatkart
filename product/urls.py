
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('store/', views.store, name='store'),
    path('search/', views.search_suggestions, name='search'),
    path('product/<int:id>', views.product_detail, name='product'),
    
]
