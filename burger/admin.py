import csv

from django.contrib import admin
from django.http import HttpResponse

from burger import models
from .models import *


# from django.contrib.auth.models import Group,User

# admin.site.unregister(Group)

admin.site.register(Cart)
admin.site.register(Voucher)

def export_reg(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registration.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'phone', 'address', 'city', 'zipcode', 'state'])
    registration = queryset.values_list('id', 'name', 'phone', 'address', 'city', 'zipcode', 'state')
    for i in registration:
        writer.writerow(i)
    return response
export_reg.short_description = 'Export to csv'


class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name','phone', 'address', 'city', 'zipcode', 'state']
    actions = [export_reg]
admin.site.register(Customer, CustomerModelAdmin)

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


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id', 'paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity','ordered_date','status','payment']
    list_editable = ['status']



@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title','thumbnail_preview']
    list_editable = ['title',]

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Image Preview'
    thumbnail_preview.allow_tags = True

def export_reg(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category(included)', 'marked_price', 'selling_price'])
    products= queryset.values_list('name', 'cart', 'marked_price', 'selling_price')
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





@admin.register(Deals)
class DealsAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['user','title','review']




