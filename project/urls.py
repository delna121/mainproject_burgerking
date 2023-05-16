"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin

from django.urls import path, include

from burger import views
from django.contrib.auth import views as auth_views

from burger.admin import ProductModelAdmin
from burger.views import sentiment_graph

admin.site.site_header="BURGER KING"
admin.site.site_title="BURGER KING"
admin.site.index_title="BURGER KING"

urlpatterns = [

    path('admin/', admin.site.urls),
    path('test/',views.test,name='test'),
    path('', include('burger.urls')),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register.html'),
    path('address/', views.address, name='address'),
    path('admin/sentiment-graph/<int:pk>/', sentiment_graph, name='sentiment-graph'),
    path('profile/', views.profile, name='profile'),
    path('orders/',views.order_detailes,name='order_detailes'),
    path('orderdetailes/',views.order,name='order'),
    path('change_password/',views.change_password,name='change_password'),
    path('logout/', auth_views.LogoutView.as_view(template_name ='logout.html'), name='logout'),
    path('show_cart/', views.show_cart, name='show_cart'),
    path('checkout/', views.checkout.as_view(), name='checkout'),
    path('rate/',views.top_rated_products,name='top_rated_products'),

    path('delivery_reg/', views.delivery_reg, name='delivery_reg'),
    path('delivery_log/', views.delivery_log, name='delivery_log'),
    path('deliveryhome/', views.deliveryhome, name='deliveryhome'),
    path('customerdetailes/<int:pk_test>/<int:order_number>/', views.customerdetailes, name='customerdetailes'),
    path('update_data/<str:pk>/', views.update_data, name='update_data'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.cart_modal, name='cart_modal'),
    # path('cart_view/',views.cart_view, name='cart_view'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
    path('show_cart/', views.show_cart, name='show_cart'),
    path('submit_review/',views.submit_review,name='submit_review'),

    path('pluscart/', views.pluscart),
    path('minuscart/', views.minuscart),
    path('remove_ad/<int:id>', views.remove_ad,name='remove_ad'),
    path('de_cart/<int:id>/', views.de_cart,name='de_cart'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('prebook/',views.prebook, name='prebook'),
    path('sales_today',views.sales_today,name='sales_today'),
    path('reviewdata/<int:order_number>/', views.rate_delivery_boy, name='reviewdata'),

    path('couponbulk/',views.couponbulk,name='couponbulk'),
    path('categorybulk/',views.categorybulk,name='categorybulk'),
    path('productbulk/',views.productbulk,name='productbulk'),




]
