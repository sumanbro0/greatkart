
from django.urls import path
from . import views
urlpatterns = [    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('profile/', views.my_profile, name='profile'),
    path("me/", views.me, name="me"),
    path("orders/", views.orders, name="orders"),
    path("address/", views.add_address, name="address"),
    path("address/<int:pk>/", views.delete_address, name="delete_address"),
]
