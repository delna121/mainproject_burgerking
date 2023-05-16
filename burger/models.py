from django.db.models import Count, Avg
from django.http import HttpResponse
from django.utils import timezone
from textblob import TextBlob
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
import io
from collections import Counter
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import User
from django.utils.html import mark_safe



STATE_CHOICES = (
    ("Andhra Pradesh","Andhra Pradesh"),
    ("Arunachal Pradesh ","Arunachal Pradesh "),
    ("Assam","Assam"),
    ("Bihar","Bihar"),
    ("Chhattisgarh","Chhattisgarh"),
    ("Chandigarh","Chandigarh"),
    ("Goa","Goa"),
    ("Gujarat","Gujarat"),
    ("Haryana","Haryana"),
    ("Himachal Pradesh","Himachal Pradesh"),
    ("Jammu and Kashmir ","Jammu and Kashmir "),
    ("Jharkhand","Jharkhand"),
    ("Karnataka","Karnataka"),
    ("Kerala","Kerala"),
    ("Madhya Pradesh","Madhya Pradesh"),
    ("Maharashtra","Maharashtra"),
    ("Manipur","Manipur"),
    ("Meghalaya","Meghalaya"),
    ("Mizoram","Mizoram"),
    ("Nagaland","Nagaland"),
    ("Odisha","Odisha"),
    ("Punjab","Punjab"),
    ("Rajasthan","Rajasthan"),
    ("Sikkim","Sikkim"),
    ("Tamil Nadu","Tamil Nadu"),
    ("Telangana","Telangana"),
    ("Tripura","Tripura"),
    ("Uttar Pradesh","Uttar Pradesh"),
    ("Uttarakhand","Uttarakhand"),
    ("West Bengal","West Bengal"),

)
CITY_CHOICES = (

    ("Pathanamthitta ", "Pathanamthitta "),


)
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=14,default=True)
    address = models.CharField(max_length=200)
    city = models.CharField(choices=CITY_CHOICES, max_length=60)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=60)

    def __str__(self):
        return self.name

STATUS_CHOICES = (
    ('Rejected','Rejected'),
    ('Accepted','Accepted'),
    ('Offline Verification processing','Offline Verification processing'),
    ('Pending','Pending'),

)


class Profile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=200)
    phone =models.CharField(max_length=14)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    zipcode=models.CharField(max_length=14)


    # latitude=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    # longitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)

    def __str__(self):
        return self.name


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=200)
    descripsion = models.CharField(max_length=200)
    category_image = models.ImageField(upload_to='cat-photo')

    def __str__(self):
        return self.title

    @property
    def thumbnail_preview(self):
        if self.category_image:
            return mark_safe('<img src="{}" width="100" height="100" />'.format(self.category_image.url))
        return ""

import matplotlib.pyplot as plt

class Product(models.Model):
    name = models.CharField(max_length=200)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    veg_status =models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def thumbnail_preview(self):
        if self.product_image:
            return mark_safe('<img src="{}" width="100" height="100" />'.format(self.product_image.url))
        return ""

    def update_rating(self):
        reviews = self.review_set.all()
        count = reviews.count()
        if count == 0:
            self.rating = None
        else:
            sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg'] or 0
            if sentiment_avg >= 0.6:
                self.rating = 5.0
            elif sentiment_avg >= 0.4:
                self.rating = 4.0
            elif sentiment_avg >= -0.3:
                self.rating = 3.0
            elif sentiment_avg >= -0.1:
                self.rating = 2.0
            else:
                self.rating = 1.0
        self.save()

        @classmethod
        def top_rated(cls, limit=5):
            return cls.objects.filter(rating__isnull=False).order_by('-rating')[:limit]
#
# class Review(models.Model):
#     RATING_CHOICES = (
#         (5, '5 stars'),
#         (4, '4 stars'),
#         (3, '3 stars'),
#         (2, '2 stars'),
#         (1, '1 star'),
#     )
#
#     SENTIMENT_CHOICES = (
#         ('hp', 'Highly Positive'),
#         ('hn', 'Highly Negative'),
#         ('p', 'Positive'),
#         ('n', 'Negative'),
#         ('ne', 'Neutral')
#     )
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     rating = models.IntegerField(choices=RATING_CHOICES)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     sentiment_polarity = models.FloatField(null=True, blank=True)
#     sentiment = models.CharField(choices=SENTIMENT_CHOICES, max_length=2, null=True, blank=True)
#
#     def save(self, *args, **kwargs):
#         blob = TextBlob(self.message)
#         self.sentiment_polarity = blob.sentiment.polarity
#
#         if self.sentiment_polarity > 0.5:
#             self.sentiment = 'hp'
#         elif self.sentiment_polarity > 0:
#             self.sentiment = 'p'
#         elif self.sentiment_polarity < -0.5:
#             self.sentiment = 'hn'
#         elif self.sentiment_polarity < 0:
#             self.sentiment = 'n'
#         else:
#             self.sentiment = 'ne'
#
#         super().save(*args, **kwargs)
#
#

    # def sentiment_category(self):
    #     if self.sentiment_score is None:
    #         return 'Unknown'
    #     if self.sentiment_score >= 0.9:
    #         return 'HP'
    #     elif self.sentiment_score >= 0.7:
    #         return 'P'
    #     elif self.sentiment_score >= 0.5:
    #         return 'N'
    #     elif self.sentiment_score >= 0.3:
    #         return 'Neg'
    #     else:
    #         return 'HN'


STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),

)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.razorpay_order_id

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

class Delivery_login(models.Model):
    user= models.EmailField(max_length=200,primary_key=True,unique=True,default=1)
    password= models.CharField(max_length=200)
    status =models.BooleanField(max_length=100,default=False)

    def __str__(self):
        return self.user
@receiver(post_save, sender=Delivery_login)
def send_delivery_boy_acceptance_email(sender, instance, **kwargs):
    if instance.status == True:
        delivery_boy = Delivery_reg.objects.get(email=instance.user)
        subject = 'Delivery boy registration accepted'
        message = 'Dear {},\n\n Lets Join Together!!...Your registration as a delivery boy has been accepted.'.format(
            delivery_boy.first_name)
        from_email = 'delnaannajoy2023a@mca.ajce.in'
        recipient_list = [delivery_boy.email]
        send_mail(subject, message, from_email, recipient_list)


def generate_order_number():
    last_order = OrderPlaced.objects.last()
    if last_order:
        return last_order.order_number + 1
    else:
        return 1000  # starting number

class OrderPlaced(models.Model):
    MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.IntegerField(default=generate_order_number, unique=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='Pending')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_boy = models.ForeignKey(Delivery_login, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    addres = models.CharField(max_length=50, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)


    def __str__(self):
        return f'{self.order_number}  - {self.user.username}'

    @property
    def total_cost(self):
        return sum(item.total_cost for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(OrderPlaced, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price



class Deals(models.Model):
    name= models.TextField(max_length='250',blank=True)
    image= models.ImageField(upload_to='deals',blank=False)
    class Meta:
        verbose_name='Deal'
        verbose_name_plural='Deals'
    def  __str__(self):
        return '{}'.format(self.name)

class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='media', null=True, blank=True)


    def __str__(self):
        return str(self.user)


class Voucher(models.Model):
    coupon_code= models.CharField(max_length=10)
    is_expired= models.BooleanField(default=False)
    discount_amt = models.IntegerField(default=100)
    minimum_amt = models.IntegerField(default=500)
    def __str__(self):
        return str(self.coupon_code)

import datetime

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.IntegerField()
    valid_from = models.DateTimeField(default=datetime.datetime.now)
    valid_to = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=30))
    is_expired= models.BooleanField(default=False)
    minimum_amt = models.IntegerField(default=500)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class Cart(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return str(self.user)

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price

    def send_coupon_notification(self):
        user_email = self.user.email
        subject = 'New Coupon Available'
        message = f"Hello,\n\nWe have added a new coupon code: {self.coupon.code}\n\nHappy shopping!"
        from_email = 'your_email@gmail.com'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)

    def send_cart_reminder(self):
        user_email = self.user.email
        subject = 'Reminder: Products in Your Cart'
        message = f"Hello,\n\nYou have the following products in your cart:\n\n"
        message += f"- {self.product.name} (Quantity: {self.quantity})\n"
        message += "\nPlease complete your purchase.\n\nHappy shopping!"
        from_email = 'your_email@gmail.com'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)




class Delivery_reg(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email =models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    pin = models.CharField(max_length=200)
    user=models.ForeignKey(Delivery_login,on_delete=models.SET_NULL,blank=True,null=True)
    aadhar_card = models.CharField(max_length=200)
    password = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Delivery_Boy Details"


class ReviewData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_boy= models.ForeignKey(Delivery_login, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='media', null=True, blank=True)
    sentiment_polarity = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        self.sentiment_polarity = self.get_sentiment()
        print('Saving ReviewData:', self)
        super().save(*args, **kwargs)

    def get_sentiment(self):
        blob = TextBlob(self.review)
        sentiment_polarity = blob.sentiment.polarity
        return sentiment_polarity

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_polarity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        self.sentiment_polarity = self.get_sentiment()
        super().save(*args, **kwargs)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.product.update_rating()

    def get_sentiment(self):
        blob = TextBlob(self.message)
        sentiment_polarity = blob.sentiment.polarity
        return sentiment_polarity



class PreBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    place = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    date = models.DateField()


class PreBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    pincode = models.CharField(max_length=7)
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Analysis(models.Model):
    name = models.ForeignKey(Delivery_login,on_delete=models.CASCADE)

class Sales(models.Model):
    date = models.DateField()
    item = models.CharField(max_length=50)
    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

class test(models.Model):
    name=models.CharField(max_length=50)
class Visit(models.Model):
    date = models.DateField(default=timezone.now)