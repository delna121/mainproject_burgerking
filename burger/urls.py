from django.contrib import admin
from django.urls import path, include
from burger import views
from .admin import Delivery_logAdmin
from .views import*
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from burger.admin import Delivery_logAdmin


urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:cid>/', views.showcategory, name='category'),
    path('register/', views.register, name='register.html'),
    path('verification/', views.verification, name='verification'),
    path('send_otp', views.send_otp, name='send otp'),

    path('change_password/',views.change_password,name='change_password'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name ='logout.html'), name='logout'),

    path('profile/', views.profile,name='profile'),
    path('filter/',views.filter,name='filter'),
    path('address/', views.address, name='address'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),

    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
    path('show_cart/', views.show_cart, name='show_cart'),

    path('pluscart/', views.pluscart),
    path('minuscart/', views.minuscart),
    path('remove_ad/<int:id>', views.remove_ad,name='remove_ad'),
    path('de_cart/<int:id>/', views.de_cart,name='de_cart'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),

    path('reviewdata/<int:order_number>/', views.rate_delivery_boy, name='reviewdata'),
    path('checkout/', views.checkout.as_view(), name='checkout'),
    path('paymentdone/',views.payment_done,name='paymentdone'),

    path('orderdetailes/',views.order,name='order'),

    # delivery_Boy
    path('delivery_reg/',views.delivery_reg,name='delivery_reg'),
    path('delivery_log/',views.delivery_log,name='delivery_log'),
    path('deliveryhome/',views.deliveryhome,name='deliveryhome'),
    path('customerdetailes/<int:pk_test>/<int:order_number>/', views.customerdetailes, name='customerdetailes'),
    path('update_data/<str:pk>/',views.update_data,name='update_data'),



    path('password_reset/',auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('admin/burger/delivery_login/sentiment-graph/', admin.site.admin_view(Delivery_logAdmin.sentiment_graph), name='sentiment-graph'),
    path('my_form', views.my_form, name='my_form'),
    path('my_post', views.my_post, name='my_post'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)