from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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
    ("Alappuzha", "Alappuzha"),
    ("Ernakulam ", "Ernakulam "),
    ("Idukki", "Idukki"),
    ("Kannur", "Kannur"),
    ("Kasaragod", "Kasaragod"),
    ("Kollam", "Kollam"),
    ("Kottayam", "Kottayam"),
    ("Kozhikode", "Kozhikode"),
    ("Malappuram", "Malappuram"),
    ("Palakkad", "Palakkad"),
    ("Pathanamthitta ", "Pathanamthitta "),
    ("Thiruvananthapuram", "Thiruvananthapuram"),
    ("Thrissur", "Thrissur"),
    ("Wayanad", "Wayanad"),

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

class Profile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=200)
    phone =models.CharField(max_length=14)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    zipcode=models.CharField(max_length=14)

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



class Product(models.Model):
    name = models.CharField(max_length=200)
    # category = models.CharField(max_length=250,default=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()

    def __str__(self):
        return self.name




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

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
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
    star =models.IntegerField(default=False)


    def __str__(self):
        return str(self.user)


class Voucher(models.Model):
    coupon_code= models.CharField(max_length=10)
    is_expired= models.BooleanField(default=False)
    discount_amt = models.IntegerField(default=100)
    minimum_amt = models.IntegerField(default=500)
    def __str__(self):
        return str(self.coupon_code)

class Cart(models.Model):
    coupon =models.ForeignKey(Voucher, on_delete=models.SET_NULL,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return str(self.user)

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price





