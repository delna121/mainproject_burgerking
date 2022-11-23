from django.contrib import admin
from django.urls import path, include
from burger import views
from .views import*
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:cid>/', views.showcategory, name='category'),
    path('register/', views.register, name='register.html'),
    path('verification/', views.verification, name='verification'),
    path('send_otp', views.send_otp, name='send otp'),

    path('change_password/',views.change_password,name='change_password'),
    path('login/', views.login, name='login'),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name ='logout.html'), name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    # path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/', views.profile,name='profile'),
    path('address/', views.address, name='address'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('show_cart/', views.show_cart, name='show_cart'),
    path('emptycart/', views.show_cart, name='emptycart'),
    path('pluscart/', views.pluscart),
    path('minuscart/', views.minuscart),
    path('remove_ad/<int:id>', views.remove_ad,name='remove_ad'),
    path('de_cart/<int:id>/', views.de_cart,name='de_cart'),


                  # path('de_cart/',views.de_cart,name='de_cart'),

    path('review/', views.review, name='review'),
    path('checkout/', views.checkout.as_view(), name='checkout'),
    path('paymentdone/',views.payment_done,name='paymentdone'),
    path('order/',views.order,name='order'),



    path('password_reset/',auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)