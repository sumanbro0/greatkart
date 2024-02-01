
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
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/<int:id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('generate_share_link/', views.generate_share_link, name='generate_share_link'),
    path('view_wishlist/<str:id>', views.view_wishlist, name='view_wishlist'),
    ]
