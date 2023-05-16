from django.contrib import admin, messages
from django.db.models import Avg, Count
from django.shortcuts import redirect, get_object_or_404
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Coupon
from .resources import couponResource, categoryResource, productResource
from django.urls import path, reverse
from django.http import HttpResponse

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import JsonResponse
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
import io
import matplotlib.pyplot as plt
from burger.models import Product, Review

from django.utils.html import format_html
import plotly.graph_objs as go
import plotly.offline as opy


import csv
from .models import *



admin.site.register(Cart)

class CouponAdmin(ImportExportModelAdmin):
    resource_class = couponResource
admin.site.register(Coupon, CouponAdmin)

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


@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['user','product']


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id', 'paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['user','order_number','ordered_date','status','total_amount','payment','delivery_boy']



    def has_add_permission(self, request, obj=None):
        return False
    # def has_change_permission(self, request, obj=None):
    #     if obj and obj.delivery_boy =='delivery_boy':
    #        return True

@admin.register(OrderItem)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = ['order','product','quantity']




class CategoryAdmin(ImportExportModelAdmin):
    resource_class = categoryResource
    list_display = ['id', 'title', 'thumbnail_preview']
    list_editable = ['title', ]

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Image Preview'
    thumbnail_preview.allow_tags = True
admin.site.register(Category,CategoryAdmin)



#
# @admin.register(Category)
# class CategoryModelAdmin(admin.ModelAdmin):
#     list_display = ['id', 'title','thumbnail_preview']
#     list_editable = ['title',]
#
#     def thumbnail_preview(self, obj):
#         return obj.thumbnail_preview
#
#     thumbnail_preview.short_description = 'Image Preview'
#     thumbnail_preview.allow_tags = True

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

class ProductModelAdmin(ImportExportModelAdmin):
    resource_class = productResource
    list_display = ['id', 'name', 'cat', 'marked_price', 'selling_price','thumbnail_preview','view_graph']

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    def view_graph(self, obj):
        url = reverse('admin:product-sentiment-graph', args=[obj.pk])
        if Review.objects.filter(product=obj).exists():
            return format_html('<a href="{}">View Graph</a>', url)
        else:
            return "No Reviews"

    view_graph.short_description = "Sentiment Graph"

    def sentiment_graph(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product=product)

        if reviews.exists():
            sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg'] or 0
            positive_reviews = reviews.filter(sentiment_polarity__gt=0, sentiment_polarity__lt=0.6)
            negative_reviews = reviews.filter(sentiment_polarity__lt=0, sentiment_polarity__gt=-0.2)
            neutral_reviews = reviews.filter(sentiment_polarity=0)
            highly_positive_reviews = reviews.filter(sentiment_polarity__gte=0.6)
            highly_negative_reviews = reviews.filter(sentiment_polarity__lte=-0.2)

            positive_count = positive_reviews.count()
            negative_count = negative_reviews.count()
            neutral_count = neutral_reviews.count()
            highly_positive_count = highly_positive_reviews.count()
            highly_negative_count = highly_negative_reviews.count()
            total_count = reviews.count()

            positive_percentage = round((positive_count / total_count) * 100, 2)
            negative_percentage = round((negative_count / total_count) * 100, 2)
            neutral_percentage = round((neutral_count / total_count) * 100, 2)
            highly_positive_percentage = round((highly_positive_count / total_count) * 100, 2)
            highly_negative_percentage = round((highly_negative_count / total_count) * 100, 2)

            # generate graph using matplotlib
            fig, ax = plt.subplots()
            fig.set_size_inches(15, 10)
            ax.bar(['Highly Positive', 'Positive', 'Neutral', 'Negative', 'Highly Negative'],
                   [highly_positive_percentage, positive_percentage, neutral_percentage, negative_percentage,
                    highly_negative_percentage],
                   color=['green', 'lightgreen', 'yellow', 'orange', 'red'])

            ax.set_xlabel('Sentiment')
            ax.set_ylabel('Percentage of Reviews')

            ax.set_title(
                'Sentiment Analysis  {} ({}% highly positive, {}% positive, {}% neutral, {}% negative, {}% highly negative)'.format(
                    product.name, highly_positive_percentage,positive_percentage, neutral_percentage, negative_percentage, highly_negative_percentage))

            # save graph as image and encode as base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # return HTTP response with graph as image
            response = HttpResponse(content_type='image/png')
            response.write(base64.b64decode(image))
            return response

        else:
            messages.warning(request, 'No reviews found for {}'.format(product.name))
            return redirect(reverse('admin:burger_product_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:pk>/sentiment-graph/', self.admin_site.admin_view(self.sentiment_graph),
                 name='product-sentiment-graph'),
        ]
        return custom_urls + urls

    thumbnail_preview.short_description = 'Image Preview'
    thumbnail_preview.allow_tags = True
admin.site.register(Product, ProductModelAdmin)
    # # graph
    # def view_graph(self, obj):
    #     url = reverse('admin:sentiment-graph', args=[obj.pk])
    #     if Review.objects.filter(product=obj).exists():
    #         return format_html('<a href="{}">View Graph</a>', url)
    #     else:
    #         return "No Reviews"
    #
    # view_graph.short_description = "Sentiment Graph"
    # def sentiment_graph(self, request, pk):
    #     delivery_boy = get_object_or_404(Delivery_login, pk=pk)
    #     reviews = ReviewData.objects.filter(delivery_boy=delivery_boy)
    #
    #     if reviews.exists():
    #         sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg'] or 0
    #         positive_reviews = reviews.filter(sentiment_polarity__gt=0)
    #         negative_reviews = reviews.filter(sentiment_polarity__lt=0)
    #         positive_count = positive_reviews.count()
    #         negative_count = negative_reviews.count()
    #         total_count = reviews.count()
    #         positive_percentage = round((positive_count / total_count) * 100, 2)
    #         negative_percentage = round((negative_count / total_count) * 100, 2)
    #
    #         # generate graph using matplotlib
    #         fig, ax = plt.subplots()
    #         fig.set_size_inches(10, 7)
    #         ax.bar(['Positive', 'Negative'], [positive_count, negative_count])
    #         ax.set_xlabel('Sentiment')
    #         ax.set_ylabel('Number of Reviews')
    #
    #         ax.set_title('Sentiment Analysis for {} ({}% positive, {}% negative)'.format(delivery_boy.user, positive_percentage,negative_percentage))
    #
    #         # save graph as image and encode as base64
    #         buffer = BytesIO()
    #         plt.savefig(buffer, format='png')
    #         buffer.seek(0)
    #         image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    #
    #         # return HTTP response with graph as image
    #         response = HttpResponse(content_type='image/png')
    #         response.write(base64.b64decode(image))
    #         return response
    #
    #     else:
    #         messages.warning(request, 'No reviews found for {}'.format(delivery_boy.user))
    #         return redirect(reverse('admin:delivery_login_changelist'))
    #
    #     def get_urls(self):
    #         urls = super().get_urls()
    #         custom_urls = [
    #             path('<str:pk>/sentiment-graph/', self.admin_site.admin_view(self.sentiment_graph),
    #                  name='sentiment-graph'),
    #         ]
    #         return custom_urls + urls

#
#     thumbnail_preview.short_description = 'Image Preview'
#     thumbnail_preview.allow_tags = True
# admin.site.register(Product,ProductModelAdmin)








class Delivery_regAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','phone','city','pin','aadhar_card']
admin.site.register(Delivery_reg,Delivery_regAdmin)

class Delivery_logAdmin(admin.ModelAdmin):
    list_display = ['user', 'view_graph']
    exclude = ('password',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    verbose_name_plural = "Delivery Boy Details"

    def view_graph(self, obj):
        url = reverse('admin:sentiment-graph', args=[obj.pk])
        if ReviewData.objects.filter(delivery_boy=obj).exists():
            return format_html('<a href="{}">View Graph</a>', url)
        else:
            return "No Reviews"
    view_graph.short_description = "Sentiment Graph"

    def sentiment_graph(self, request, pk):
        delivery_boy = get_object_or_404(Delivery_login, pk=pk)
        reviews = ReviewData.objects.filter(delivery_boy=delivery_boy)

        if reviews.exists():
            sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg'] or 0
            positive_reviews = reviews.filter(sentiment_polarity__gt=0)
            negative_reviews = reviews.filter(sentiment_polarity__lt=0)
            positive_count = positive_reviews.count()
            negative_count = negative_reviews.count()
            total_count = reviews.count()
            positive_percentage = round((positive_count / total_count) * 100, 2)
            negative_percentage = round((negative_count / total_count) * 100, 2)

            # send email to delivery boy based on sentiment percentage
            if positive_percentage >= negative_percentage:
                subject = 'Positive review feedback'
                message = 'Dear {},\n\nCongratulations!You are always working hard to ensure the pacakages are deliver on time and i good condition.I appreciate you work and your overall  analysis for the reviews is {}% positive.Go with it'.format(
                    delivery_boy.user, positive_percentage)
                from_email = 'delnaannajoy2023a@mca.ajce.in'
                recipient_list = [delivery_boy.user]
                send_mail(subject, message, from_email, recipient_list)
            else:
                subject = 'Negative review feedback'
                message = ' Dear {},\n\nWe have received some negative feedback about your delivery service. We take customer satisfaction very seriously and expect our delivery boys to provide excellent service. Please take steps to improve your service and prevent further negative feedback.\n\nBest regards,\nThe Delivery Team'.format(
                    delivery_boy.user, negative_percentage)
                from_email = 'delnaannajoy2023a@mca.ajce.in'
                recipient_list = [delivery_boy.user]
                send_mail(subject, message, from_email, recipient_list)

            # generate graph using matplotlib
            fig, ax = plt.subplots()
            fig.set_size_inches(10, 7)
            ax.bar(['Positive', 'Negative'], [positive_count, negative_count])
            ax.set_xlabel('Sentiment')
            ax.set_ylabel('Number of Reviews')

            ax.set_title('Sentiment Analysis for {} ({}% positive, {}% negative)'.format(delivery_boy.user, positive_percentage, negative_percentage))

            # save graph as image and encode as base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # return HTTP response with graph as image
            response = HttpResponse(content_type='image/png')
            response.write(base64.b64decode(image))
            return response

        else:
            messages.warning(request, 'No reviews found for {}'.format(delivery_boy.user))
            return redirect(reverse('admin:delivery_login_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:pk>/sentiment-graph/', self.admin_site.admin_view(self.sentiment_graph), name='sentiment-graph'),
        ]
        return custom_urls + urls
admin.site.register(Delivery_login, Delivery_logAdmin)



@admin.register(Deals)
class DealsAdmin(admin.ModelAdmin):
    list_display = ['name']





#
# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ['name','message','email','rating','created_at']
#     def has_add_permission(self, request, obj=None):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False

@admin.register(ReviewData)
class ReviewDataAdmin(admin.ModelAdmin):
    list_display = ['user','review','delivery_boy','sentiment_polarity']


class MyModelAdmin(admin.ModelAdmin):
    ...

    def sales_chart(self, request):
        products = Product.objects.all()
        data = {}
        Sum = 0
        for i in products:
            sales = OrderPlaced.objects.filter(product=i)
            if sales.exists():
                total_sales = sales.aggregate(Sum('quantity'))['quantity__sum']
                data[i.name] = total_sales or 0

        # generate graph using matplotlib
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 15)

        ax.bar(data.keys(), data.values(), color='green')
        ax.set_xlabel('Products')
        ax.set_ylabel('Total Sales')
        ax.set_title('Sales Chart')
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

            path('sales-chart/', self.admin_site.admin_view(self.sales_chart), name='sales-chart'),
        ]
        return custom_urls + urls
