
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('store/', views.store, name='store'),
    path('search/', views.search_suggestions, name='search'),
    path('product/<int:id>', views.product_detail, name='product'),
    path('add_review/<int:id>', views.add_review, name='add_review'),
    path('delete_review/<int:id>', views.delete_review, name='delete_review'),
    path('update_review/<int:id>', views.update_review, name='update_review'),
    
]
