import csv

from django.contrib import admin
from django.http import HttpResponse

from burger import models
from .models import *
# from django.contrib.auth.models import Group,User

# admin.site.unregister(Group)


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name','phone', 'address', 'city', 'zipcode', 'state']

# def export_reg(modeladmin, request, queryset):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="registration.csv"'
#     writer = csv.writer(response)
#     writer.writerow(['Email', 'Password', 'Address', 'Phone',  'State', 'Country'])
#     registration = queryset.values_list('email', 'password', 'address', 'phone',  'state', 'country')
#     for i in registration:
#         writer.writerow(i)
#     return response
#
#
# export_reg.short_description = 'Export to csv'
#
#
# class RegAdmin(admin.ModelAdmin):
#     list_display = ['email', 'password','address',  'phone',  'state', 'country']
#     actions = [export_reg]
#
#
# admin.site.register(Account,RegAdmin)






@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category_image']
    list_editable = ['title','category_image']

def export_reg(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category(included)', 'marked_price', 'selling_price'])
    products= queryset.values_list('name', 'cat', 'marked_price', 'selling_price')
    for i in products:
        writer.writerow(i)
    return response
export_reg.short_description = 'Export to csv'

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cat', 'product_image','marked_price','selling_price']
    list_editable = ['name', 'cat', 'product_image','marked_price','selling_price']
    list_per_page = 20
    actions = [export_reg]

admin.site.register(Product,ProductModelAdmin)


# class ProductModelAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'cat', 'product_image','marked_price','selling_price']
#     list_editable = ['name', 'cat', 'product_image','marked_price','selling_price']
#     list_per_page = 20
#     actions = [export_reg]


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'product', 'quantity', 'ordered_date', 'status']


@admin.register(Deals)
class DealsAdmin(admin.ModelAdmin):
    list_display = ['name']



