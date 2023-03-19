from django.contrib import admin
from django.db.models import Avg, Count
from django.urls import path, reverse
from django.http import HttpResponse
from django.http import JsonResponse
import matplotlib.pyplot as plt
from io import BytesIO
import base64


import csv

from django.utils.html import format_html

from burger import models
from .models import *


# from django.contrib.auth.models import Group,User

# admin.site.unregister(Group)

admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Profile)

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

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['user','product']


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id', 'paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['user','order_number','ordered_date','status','payment','delivery_boy']
    list_editable = ['delivery_boy']

@admin.register(OrderItem)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = ['order','product','quantity']

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


class Delivery_regAdmin(admin.ModelAdmin):
    list_display=['first_name']
    exclude=('password',)
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    verbose_name_plural = "Delivery_boy Details"
admin.site.register(Delivery_reg,Delivery_regAdmin)

class Delivery_logAdmin(admin.ModelAdmin):
    list_display = ['user']
    exclude = ('password',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    verbose_name_plural = "Delivery_Boy Details"

    def sentiment_graph(self, request):
        delivery_boys = Delivery_login.objects.all()
        data = {}
        for delivery_boy in delivery_boys:
            reviews = ReviewData.objects.filter(delivery_boy=delivery_boy)
            if reviews.exists():
                sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg']
                data[delivery_boy.user] = sentiment_avg or 0

        # generate graph using matplotlib
        fig, ax = plt.subplots()
        fig.set_size_inches(20,15)
        ax.bar(data.keys(), data.values())
        ax.set_xlabel('Delivery Boys')
        ax.set_ylabel('Average Sentiment Polarity')
        ax.set_title('Best Delivery Boys based on Sentiment Analysis')
        plt.xticks(rotation=45)

        # save graph as image and encode as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # return HTTP response with graph as image
        response = HttpResponse(content_type='image/png')
        response.write(base64.b64decode(image))
        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sentiment-graph/', self.admin_site.admin_view(self.sentiment_graph), name='sentiment-graph'),
        ]
        return custom_urls + urls


admin.site.register(Delivery_login, Delivery_logAdmin)


@admin.register(Deals)
class DealsAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(ReviewData)
@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['user','title','review']




