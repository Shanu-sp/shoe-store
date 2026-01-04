"""
URL configuration for shoes_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/', views.cart_page, name='cart'),
    path('order/', views.place_order, name='order'),
    # path('signup/', views.signup, name='signup'),  # NEW
    path('brand/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('signup/', views.signup, name='signup'),
    path('verify-signup-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('login/', views.login_request, name='login'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('checkout/',views.checkout,name='checkout'),
    path('order_success/',views.order_success,name='order_success'),
    path('cart/',views.cart_view, name='cart'),




]

