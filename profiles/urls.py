
from django.urls import path
from . import views
urlpatterns = [
    
    path('', views.index, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/', views.my_profile, name='profile'),
    path("me/", views.me, name="me"),
    path("orders/", views.orders, name="orders"),
    path("address/", views.add_address, name="address"),
]
