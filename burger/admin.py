from django.contrib import admin
from burger import models
from .models import *

# Register your models here.
#admin.site.register(Customer)

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'address', 'city', 'zipcode', 'state']


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category_image']
    list_editable = ['title','category_image']


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cat', 'product_image','marked_price','selling_price']
    list_editable = ['name', 'cat', 'product_image','marked_price','selling_price']
    list_per_page = 20


#
# @admin.register(CartItem)
# class CartModelAdmin(admin.ModelAdmin):
#     list_display = ['user','cart_id','product', 'quantity']


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'product', 'quantity', 'ordered_date', 'status']


@admin.register(Deals)
class DealsAdmin(admin.ModelAdmin):
    list_display = ['name']

