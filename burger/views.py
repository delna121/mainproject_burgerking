import json
from decimal import Decimal
from hashlib import sha256


from tensorflow.python.data import Dataset

from .resources import couponResource
from django.db import IntegrityError
from django.views.generic import DetailView
from django.db.models.functions import ExtractMonth, TruncMonth
from django.http import HttpResponse, HttpResponseBadRequest
from django import template
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from matplotlib import pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas

from .models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
# from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User,auth
from .forms import UserRegistrationForm,CustomerProfileForm,OrderForm,CouponApplyForm
from .filter import OrderplacedFilter
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import View
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Avg, Count, Sum
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
import razorpay
from django.conf import settings
from django.views.decorators.cache import never_cache

from django.core.exceptions import ObjectDoesNotExist
import math,random
import datetime

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import re
from nltk.corpus import stopwords
import pyttsx3

# nltk.download('stopwords')
# set(stopwords.words('english'))



def my_function(date_string):
    if not isinstance(date_string, str):
        return None

    try:
        parsed_date = datetime.datetime.fromisoformat(date_string)
    except ValueError:
        return None

    return parsed_date



# Create your views here.

from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

from django.template.defaultfilters import register

@register.filter
def make_range(value):
    return range(1, int(value) + 1)

def index(request):
    if 'search' in request.GET:
        search = request.GET['search']
        product = Product.objects.filter(name__icontains=search)
    else:
        product = Product.objects.all()
    categories = Category.objects.all()
    # wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
    obj = Deals.objects.all()
    review = Reviews.objects.all()
    data = {'product':product, 'categories':categories, 'result': obj,'review':review}
    return render(request, 'index.html', data)



def showcategory(request, cid):
    categories = Category.objects.all()
    obj = Deals.objects.all()
    cats = Category.objects.get(pk=cid)
    product = Product.objects.filter(cat=cats)
    data = {
        'categories':categories,
        'result': obj,
        'product': product
    }
    return render(request, 'index.html', data)
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detailes.html'
    context_object_name = 'product'


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if password == cpassword:
            if User.objects.filter(username=username).exists():
                messages.success(request, "Username alredy exist")
                return redirect('register.html')
            elif User.objects.filter(email=email).exists():
                messages.success(request, "Email alredy exist")
                return redirect('register.html')
            else:
                user=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password)
                user.save();
            print("User Created");
            messages.success(request,"Registration success!!")
            return redirect('login')
        else:
            messages.success(request,"Registration failed")
            return redirect('register.html')
    return render(request, 'register.html')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user:
            auth.login(request,user)
            request.session['username'] = username
            return redirect('index')
        else:
            messages.success(request,"invalid Username/Password")
            return redirect('login')
    return render(request,'login.html')




def generateOTP():
    digits = '0123456789'
    OTP = ''
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def send_otp(request):
    email=request.GET.get('email')
    o =generateOTP()
    htmlgen= '<p>Your OTP is <strong>'+o+'</strong></p>'
    send_mail('OTP request',o,'delnaannajoy2023a@mca.ajce.in',[email],fail_silently=False,html_message=htmlgen)
    print(o)
    return HttpResponse(o)

def verification(request):
    return render(request,'verification.html')

def filter(request):
    return render(request,'filter.html')

@login_required
def profile(request):
    if request.method == 'POST':
        usr=request.user
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        zipcode = request.POST['zipcode']


        profile =Profile(user=usr,name=name,phone=phone,address=address,city=city,zipcode=zipcode)
        profile.save()
        messages.success(request, ' updated successfully.')
        return redirect('address')
    return render(request,'profile.html')

# def review(request):
#     if request.method == "POST":
#         usr = request.user
#         title = request.POST.get('title')
#         review = request.POST.get('review')
#         image = request.FILES.get('wimg')
#         user = Reviews(title=title,review=review,image=image,user=usr)
#         user.save()
#         messages.info(request, 'Your review has been successfully send..!!')
#         return redirect('review')
#     return render(request, 'mailbox-compose.html')

from django.shortcuts import get_object_or_404, redirect, render
from .models import OrderPlaced, ReviewData


@never_cache
def sentiment_graph(request, pk):
    delivery_login = get_object_or_404(Delivery_login, pk=pk)
    reviews = ReviewData.objects.filter(delivery_boy=delivery_login)
    if reviews.exists():
        sentiment_avg = reviews.aggregate(Avg('sentiment_polarity'))['sentiment_polarity__avg']
    else:
        sentiment_avg = 0
    data = {
        'delivery_login': delivery_login,
        'sentiment_avg': sentiment_avg,
    }
    return render(request, 'burger/delivery_login_sentiment_graph.html', data)

@login_required
def rate_delivery_boy(request, order_number):
    order = get_object_or_404(OrderPlaced, order_number=order_number)
    delivery_boy = order.delivery_boy
    if request.method == 'POST':
        review = request.POST['review']
        review_data = ReviewData.objects.create(
            user=request.user,
            delivery_boy=delivery_boy,
            review=review,
        )
        return redirect(reverse_lazy('index'))
    else:
        context = {'order': order, 'delivery_boy': delivery_boy, 'delivery_boy_name': delivery_boy.user}
        return render(request, 'reviewdata.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            user = User.objects.get(email__exact=request.user.email)
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('login')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'change_password.html')


def address(request):
    address = Profile.objects.filter(user=request.user)
    return render(request, 'address.html', {'address':address})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    quantity = request.GET.get('quantity')
    print(f"Quantity: {quantity}")
    if not quantity or not quantity.isdigit() or int(quantity) <= 0:
        messages.error(request, "Invalid quantity")
        return redirect('index')
    product = Product.objects.get(id=product_id)
    try:
        Cart(user=user, product=product, quantity=quantity or 1).save()
        messages.success(request, "Added to cart successfully")
    except IntegrityError:
        messages.error(request, "Invalid quantity")
    return redirect('index')


def cart_modal(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('id')
        return render(request, 'cart_modal.html', {'cart': cart})

    # cart_items = Cart.objects.filter(user=request.user)
    # return render(request, 'cart_modal.html', {'cart_items': cart_items})

# @login_required
# def cart_view(request):
#     user = request.user
#     cart_items = Cart.objects.filter(user=user)
#     return render(request, 'cart.html', {'cart_items': cart_items})

from django.db.models import Avg




@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('id')
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        coupon_code = request.session.get('coupon_code', None)
        coupon_applied = False  # added variable to track coupon status

        # Get top rated products
        products = Product.objects.filter(rating__isnull=False).order_by('-rating')[:4]

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.valid_to > timezone.now():
                    amount = sum([p.quantity * p.product.selling_price for p in cart_product])
                    discount = coupon.discount / 100 * amount
                    total_amount = amount + shipping_amount - discount
                    coupon_applied = True  # set coupon_applied to True
                else:
                    coupon_code = None
                    del request.session['coupon_code']
            except Coupon.DoesNotExist:
                coupon_code = None
                del request.session['coupon_code']
        if not coupon_code:
            amount = sum([p.quantity * p.product.selling_price for p in cart_product])
            total_amount = amount + shipping_amount
        context = {
            'cart': cart,
            'total_amount': total_amount,
            'amount': amount,
            'coupon_code': coupon_code,
            'coupon_applied': coupon_applied,  # pass coupon_applied to template
            'products': products,  # include top rated products in context
        }
        return render(request, 'addtocart.html', context)
    else:
        return redirect(login)


def top_rated_products(request):
    products = Product.objects.filter(rating__isnull=False).order_by('-rating')[:3]
    return render(request, 'top_rated_products.html', {'products': products})

def couponbulk(request):
    if request.method == 'POST':
        coupon_resource = couponResource()
        dataset = Dataset()
        new_staff = request.FILES['myfile']
        if not new_staff.name.endswith('xlsx'):
            messages.info(request,'Wrong Format')
            return render(request,'Admin/couponbulk.html')
        imported_data = dataset.load(new_staff.read(),format='xlsx')
        for data in imported_data:
            value = Coupon(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],


            )
            value.save()
    return render(request,'Admin/couponbulk.html')

def productbulk(request):
    if request.method == 'POST':
        staff_resource = categorybulk()
        dataset = Dataset()
        new_staff = request.FILES['myfile']
        if not new_staff.name.endswith('xlsx'):
            messages.info(request,'Wrong Format')
            return render(request,'Admin/productbulk.html')
        imported_data = dataset.load(new_staff.read(),format='xlsx')
        for data in imported_data:
            value = Category(
                data[0],
                data[1],
                data[2],
            )
            value.save()
    return render(request,'Admin/productbulk.html')

def categorybulk(request):
    if request.method == 'POST':
        staff_resource = categorybulk()
        dataset = Dataset()
        new_staff = request.FILES['myfile']
        if not new_staff.name.endswith('xlsx'):
            messages.info(request,'Wrong Format')
            return render(request,'Admin/categorybulk.html')
        imported_data = dataset.load(new_staff.read(),format='xlsx')
        for data in imported_data:
            value = Category(
                data[0],
                data[1],
                data[2],
            )
            value.save()
    return render(request,'Admin/categorybulk.html')
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            request.session['coupon_code'] = coupon_code
            cart_items = Cart.objects.filter(user=request.user)
            for item in cart_items:
                item.coupon = coupon
                item.save()
            messages.success(request, "Coupon Applied Successfully")
        except Coupon.DoesNotExist:
            return redirect('remove_coupon')
            messages.warning(request,' Coupon removed')
    return redirect('show_cart')


@login_required
def remove_coupon(request):
    request.session.pop('coupon_code',None)
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.coupon=None
        item.save()
    messages.success(request,'Coupon removed successfully')
    return redirect('show_cart')


@login_required
def pluscart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            subtotal = (p.quantity * p.product.selling_price)
            amount += subtotal
            data ={
                'quantity': c.quantity,
                'amount': amount,
                'total_amount': amount + shipping_amount
                }
        return JsonResponse(data)

@login_required
def minuscart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        if c.quantity > 1:
            c.quantity -= 1
            c.save()
            amount = 0.0
            shipping_amount = 70.0
            total_amount = 0.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            subtotal = (p.quantity * p.product.selling_price)
            amount += subtotal
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def remove_ad(request, id):
    user = request.user
    cart = Profile.objects.filter(user_id=user)
    if cart.exists():
        Profile.objects.get(id=id).delete()
        # messages.warning(request, "This address is removed!!!")
        # messages.info(request, "You don't have an active order")
        return redirect('/address')


from django.shortcuts import render, redirect
from django.contrib import messages

# def prebook(request):
#     user = request.user
#     cart = Cart.objects.filter(user=request.user)
#     amount = 0
#     shipping_amount = 70
#     coupon_code = request.session.get('coupon_code')
#     cart_product = Cart.objects.filter(user=request.user)
#     razor_amount = 0  # Define a default value for razor_amount
#
#     if cart_product:
#         for p in cart_product:
#             subtotal = p.quantity * p.product.selling_price
#             amount = amount + subtotal
#
#             if coupon_code:
#                 try:
#                     coupon = Coupon.objects.get(code=coupon_code)
#                     if coupon.valid_to > timezone.now():
#                         discount = coupon.discount / 100 * amount
#                         amount = amount - discount
#                 except Coupon.DoesNotExist:
#                     pass
#
#         total_amount = amount + shipping_amount
#
#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(code=coupon_code)
#                 if coupon.valid_to > timezone.now():
#                     discount = coupon.discount / 100 * amount
#                     total_amount = amount - discount
#             except Coupon.DoesNotExist:
#                 pass
#
#         if request.method == 'POST':
#             # Get the shipping address details from the form
#             name = request.POST.get('name')
#             phone = request.POST.get('phone')
#             address = request.POST.get('address')
#             place = request.POST.get('place')
#             pincode = request.POST.get('pincode')
#             date = request.POST.get('date')
#
#             # Update the prebook object with the shipping address details
#             prebook.name = name
#             prebook.phone = phone
#             prebook.address = address
#             prebook.place = place
#             prebook.pincode = pincode
#             prebook.date = date
#
#             prebook.save()
#
#             # Create Razorpay order and payment objects and save the payment details
#         razor_amount = total_amount * 100
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         data = {"amount": razor_amount, "currency": "INR", "receipt": "order_rcptid_11"}
#         payment_response = client.order.create(data=data)
#         order_id = payment_response['id']
#         request.session['order_id'] = order_id
#         order_status = payment_response['status']
#         if order_status == 'created':
#             payment = Payment(
#                 user=user,
#                 amount=total_amount,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_status=order_status
#             )
#             payment.save()
#
#         context = {
#             'cart': cart,
#             'total_amount': total_amount,
#             'coupon_code': coupon_code,
#             'razor_amount': razor_amount,
#         }
#
#         # Render the prebooking.html template with the context
#         return render(request, 'prebooking.html', context)
#     else:
#         return redirect('cart')

def prebook(request):
    user = request.user
    cart = Cart.objects.filter(user=request.user)
    amount = 0
    shipping_amount = 70
    coupon_code = request.session.get('coupon_code')
    cart_product = Cart.objects.filter(user=request.user)
    razor_amount = 0  # Define a default value for razor_amount

    if cart_product:
        for p in cart_product:
            subtotal = p.quantity * p.product.selling_price
            amount = amount + subtotal

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.valid_to > timezone.now():
                        discount = coupon.discount / 100 * amount
                        amount = amount - discount
                except Coupon.DoesNotExist:
                    pass

        total_amount = amount + shipping_amount

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.valid_to > timezone.now():
                    discount = coupon.discount / 100 * amount
                    total_amount = amount - discount
            except Coupon.DoesNotExist:
                pass

        if request.method == 'POST':
            # Get the shipping address details from the form
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            place = request.POST.get('place')
            pincode = request.POST.get('pincode')
            date = request.POST.get('date')

            # Retrieve the prebook object from the database or create a new one
            try:
                prebook = PreBooking.objects.get(user=user)
            except PreBook.DoesNotExist:
                prebook = PreBooking(user=user)

            # Update the prebook object with the shipping address details
            prebook.name = name
            prebook.phone = phone
            prebook.address = address
            prebook.place = place
            prebook.pincode = pincode
            prebook.date = date

            prebook.save()

            # Create Razorpay order and payment objects and save the payment details
        razor_amount = total_amount * 100
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razor_amount, "currency": "INR", "receipt": "order_rcptid_11"}
        payment_response = client.order.create(data=data)
        order_id = payment_response['id']
        request.session['order_id'] = order_id
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=total_amount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()

        context = {
            'cart': cart,
            'total_amount': total_amount,
            'coupon_code': coupon_code,
            'razor_amount': razor_amount,
        }

        # Render the prebooking.html template with the context
        return render(request, 'prebooking.html', context)
    else:
        return redirect('cart')


class checkout(View):
    def get(self, request):
        user = request.user
        address = Profile.objects.filter(user=request.user)
        cart = Cart.objects.filter(user=request.user)
        amount = 0
        shipping_amount = 70
        coupon_code = request.session.get('coupon_code')
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                subtotal = p.quantity * p.product.selling_price
                amount = amount + subtotal

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.valid_to > timezone.now():
                        discount = coupon.discount / 100 * amount
                        amount = amount - discount
                except Coupon.DoesNotExist:
                    pass

            total_amount = amount + shipping_amount

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.valid_to > timezone.now():
                        discount = coupon.discount / 100 * amount
                        discounted_amount = amount - discount
                except Coupon.DoesNotExist:
                    pass

            razor_amount = total_amount * 100
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = {"amount": razor_amount, "currency": "INR", "receipt": "order_rcptid_11"}
            payment_response = client.order.create(data=data)
            order_id = payment_response['id']
            request.session['order_id'] = order_id
            order_status = payment_response['status']
            if order_status == 'created':
                payment = Payment(
                    user=user,
                    amount=total_amount,
                    razorpay_order_id=order_id,
                    razorpay_payment_status=order_status
                )

                payment.save()

            context = {
                'address': address,
                'cart': cart,
                'total_amount': total_amount,
                'razor_amount': razor_amount,
                'coupon_code': coupon_code,
            }
            return render(request, 'checkout.html', context)
        else:
            return redirect('cart')



def payment_done(request):
    order_id = request.session['order_id']
    payment_id = request.GET.get('payment_id')

    print(payment_id)
    cust_id = request.GET.get('cust_id')
    user = request.user
    payment = Payment.objects.get(razorpay_order_id=order_id)

    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    cart = Cart.objects.filter(user=user)
    total_amount_paid = payment.amount  # convert amount from paise to rupees
    order = OrderPlaced.objects.create(user=user, payment=payment,total_amount=total_amount_paid)

    for c in cart:
        OrderItem.objects.create(order=order, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('order_detailes')

@login_required
def order_detailes(request):
    latest_order = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date').first()
    context = {'latest_order': latest_order}
    return render(request, 'currentorder.html', context)
@login_required
def order(request):
    order_placed = OrderPlaced.objects.filter(user=request.user, status='delivered').order_by('id').reverse()
    return render(request,'orderdetailes.html',locals())
@login_required
def de_cart(request, id):
    user = request.user
    cart = Cart.objects.filter(user_id=user)
    if cart.exists():
        Cart.objects.get(id=id).delete()
        messages.warning(request, "This product is removed form your cart")
        # messages.info(request, "You don't have an active order")
        return redirect('show_cart')

def delivery_reg(request):
    if request.method == 'POST':
        first_name= request.POST.get('fname')
        last_name = request.POST.get('lname')
        email= request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        pin = request.POST.get('pin')
        aadhar_card = request.POST.get('aadhar')
        password= request.POST.get('pass1')
        password2 = request.POST.get('pass2')
        pass8 = sha256(password2.encode()).hexdigest()

        if Delivery_login.objects.filter(user=email).exists():
            messages.success(request,'Already exist email id')
            return redirect(delivery_reg)
        else:
            log=Delivery_login(user=email,password=pass8)
            log.save()
            userid=Delivery_login(user=email)
            reg=Delivery_reg(first_name=first_name,last_name=last_name,phone=phone,email=email,city=city,user_id=userid.user,pin=pin,aadhar_card=aadhar_card,password=pass8)
            reg.save()
            return redirect('delivery_log')
    return render(request, 'delivery.html')

def delivery_log(request):
    request.session.flush()
    if 'email' in request.session:
        return redirect(deliveryhome)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        passwords = sha256(password.encode()).hexdigest()
        delivery = Delivery_login.objects.filter(user=email,password=passwords,status=1)
        if delivery:
            delivery_detailes = Delivery_login.objects.get(user=email,password=passwords)
            email= delivery_detailes.user
            request.session['email'] = email
            return redirect(deliveryhome)
        else:
            messages.success(request,"Invalid Credentials")
            return redirect(delivery_log)
    return render(request,'delivery_log.html')

def deliveryhome(request):
    if 'email' in  request.session:
        email = request.session['email']
        detailes = OrderPlaced.objects.filter(delivery_boy=email).order_by('id').reverse()
        profile = Profile.objects.all()
        total_order = OrderPlaced.objects.filter(delivery_boy=email).count()
        myFilter = OrderplacedFilter(request.GET,queryset=detailes)
        detailes = myFilter.qs
        print(total_order)
        # count = MyModel.objects.filter(status='active').count()
        delivered = OrderPlaced.objects.filter(delivery_boy=email, status='delivered').count()
        print(delivered)
        pending = OrderPlaced.objects.filter(status='pending').count()
        print(pending)
        return render(request,'deliveryhome.html',{'name':email,'myFilter':myFilter,'detailes':detailes,'profile':profile,'total_orders':total_order,'delivered':delivered,'pending':pending})
    return redirect(delivery_log)

def customerdetailes(request, pk_test, order_number):
    if 'email' in request.session:
        email = request.session['email']
    customer = Profile.objects.filter(user_id=pk_test)
    orders = OrderPlaced.objects.filter(user_id=pk_test, order_number=order_number)
    if orders.exists():
        order = orders.first()
        order_items = order.items.all()
        total_order = orders.count()
    else:
        order_items = []
        total_order = 0
    return render(request, 'customerdetailes.html', {'name': email, 'customer': customer, 'order': order, 'total_order': total_order, 'order_items': order_items})

    # myFilter = OrderplacedFilter(request.GET,queryset=order)
    # order=myFilter.qs
    # order_number = request.GET.get('order_number')
    # order_items = OrderItem.objects.filter(order__order_number=order_number)
    # return render(request,'customerdetailes.html',{'name':email,'customer':customer,'order':order,'total_order':total_order,'order_items': order_items})

def update_data(request,pk):
    if 'email' in request.session:
        email = request.session['email']
        order = OrderPlaced.objects.get(id=pk)
        form = OrderForm(instance=order)
        if request.method == 'POST':
            form =OrderForm(request.POST,instance=order)
            if form.is_valid():
                form.save()
                return redirect(deliveryhome)
    return render(request,'update_data.html',{'name':email,'form':form})


def my_form(request):
    engine = pyttsx3.init()
    engine.say('Hello, Welcome to the feedback section.')
    engine.runAndWait()
    return render(request, 'form.html')


def my_post(request):
    if request.method == 'POST':
        stop_words = stopwords.words('english')
        # my contribution
        stop_words.remove('very')
        stop_words.remove('not')

        # convert to lowercase
        text1 = request.POST['text1'].lower()

        # my contribution
        text_final = ''.join(i for i in text1 if not i.isdigit())
        net_txt = re.sub('[^a-zA-Z0-9\n]', ' ', text_final)

        # remove stopwords
        processed_doc1 = ' '.join([i for i in net_txt.split() if i not in stop_words])

        sa = SentimentIntensityAnalyzer()
        dd = sa.polarity_scores(text=processed_doc1)
        compound = round((1 + dd['compound']) / 2, 2)
        final = compound * 100

        if "enough" in text1 or "sufficient" in text1 or "ample" in text1 or "abudant" in text1:
            engine = pyttsx3.init()
            engine.say('You liked us by' + str(final) + '% Thank you for your valuable response')
            engine.runAndWait()

            return render(request, 'form.html', {'final': final, 'text1': net_txt})

        elif final == 50:
            engine = pyttsx3.init()
            engine.say('Please enter an adequate resposnse, Thank You')
            engine.runAndWait()
            return render(request, 'form.html', {'final': final, 'text1': net_txt})
        else:
            engine = pyttsx3.init()
            engine.say('You liked us by' + str(final) + '% Thank you for your valuable response')
            engine.runAndWait()
            if final > 50:

                return render(request, 'form.html', {'final': final, 'text1': net_txt})
            elif final < 50:

                return render(request, 'form.html', {'final': final, 'text1': net_txt})
            else:

                return render(request, 'form.html', {'final': final, 'text1': net_txt})
    else:
        return redirect('my_form')

# def sales_report(request):
#     sales = Sales.objects.filter(date__range=[start_date, end_date])
#     total_sales = sales.aggregate(models.Sum('total_amount'))
#     context = {'sales': sales, 'total_sales': total_sales}
#     return render(request, 'sales_report.html', context)

def submit_feedback(request):
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        # Do something with the feedback (e.g. save it to the database)
        return render(request, 'index')


def test(request):
    return render(request,'test.html')
import matplotlib
matplotlib.use('Agg')


@csrf_exempt
@user_passes_test(is_admin)
def view(request):
    # Get some data to display in other parts of the template
    if not request.user.is_superuser:
        Visit.objects.create()
    today = timezone.now().date()
    customer = User.objects.filter(is_staff=False).count()
    delivery_boy = Delivery_login.objects.filter(status=True).count()
    delivered = OrderPlaced.objects.filter(status='Delivered').count()
    num_visits = Visit.objects.filter(date=today).count()
    total_paid_amount = Payment.objects.filter(paid=True).aggregate(Sum('amount'))['amount__sum']

    # Get the sales data for the line graph
    data = OrderPlaced.objects.annotate(month=TruncMonth('ordered_date')).filter(payment__paid=True).values(
        'month').annotate(total_sales=Sum('payment__amount')).order_by('month')

    months = [d['month'].strftime('%B %Y') for d in data]
    total_sales = [d['total_sales'] for d in data]

    chart_data = {
        'labels': months,
        'data': total_sales,
    }

    # Render the template with the chart data and other context variables
    context = {
        'chart_data': json.dumps(chart_data),
        'customer': customer,
        'delivery_boy': delivery_boy,
        'delivered': delivered,
        'total_paid_amount': total_paid_amount,
        'num_visits': num_visits,
    }
    return render(request, 'admin/products_sold_by_month.html', context)


#
# def get_sales_data():
#     data = OrderPlaced.objects.annotate(month=TruncMonth('ordered_date')).values(
#         'month').annotate(total_sales=Count('id')).order_by('month')
#
#     months = [d['month'].strftime('%B %Y') for d in data]
#     total_sales = [d['total_sales'] for d in data]
#
#     return {'months': months, 'total_sales': total_sales}
#
# @csrf_exempt
# def view(request):
#     customer = User.objects.filter(is_staff=False).count()
#     delivery_boy = Delivery_login.objects.filter(status=True).count()
#     delivered = OrderPlaced.objects.filter(status='Delivered').count()
#     total_paid_amount = Payment.objects.filter(paid=True).aggregate(Sum('amount'))['amount__sum']
#
#     data = OrderPlaced.objects.annotate(month=ExtractMonth('ordered_date')).values(
#         'month').annotate(total=Count('id')).order_by('month')
#
#     months = [month[1] for month in OrderPlaced.MONTH_CHOICES]
#
#     totals = [data.filter(month=month[0]).aggregate(total=Count('id'))['total'] for month in OrderPlaced.MONTH_CHOICES]
#
#     chart_data = {
#         'labels': months,
#         'data': totals,
#     }
#
#     # Render the template with the chart data and other context variables
#     context = {
#         'chart_data': json.dumps(chart_data),
#         'customer': customer,
#         'delivery_boy':delivery_boy,
#         'delivered':delivered,
#         'total_paid_amount':total_paid_amount
#     }
#     return render(request, 'admin/products_sold_by_month.html', context)

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Review

# def submit_review(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         rating = request.POST.get('rate')
#         message = request.POST.get('message')
#         review = Review(name=name, email=email, rating=rating, message=message)
#         review.save()
#         return HttpResponseRedirect('/thank-you/')
#     return render(request, 'index.html')
def submit_review(request):
    user = request.user
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        review = Review(user=user, product_id=product_id, name=name, email=email, message=message)
        review.save()
        messages.success(request,"Thank you for your valued review")
        return redirect('index')
    return render(request, 'product_details.html')


# def sales_today(request):
#     today = timezone.now().date()
#     orders = OrderPlaced.objects.filter(ordered_date__date=today, status='Delivered')
#     total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
#     context = {
#         'orders': orders,
#         'total_sales': total_sales,
#     }
#     return render(request, 'sales_today.html', context)
from django.db.models import Sum
from django.db.models import Sum
from django.utils import timezone

def sales_today(request):
    # Get today's date
    today = timezone.now().date()

    # Get all orders with a status of "Delivered" for today's date
    delivered_orders = OrderPlaced.objects.filter(status='Delivered', ordered_date__date=today)

    # Get all items in those orders
    order_items = OrderItem.objects.filter(order__in=delivered_orders)

    # Get the total sales count for today
    total_sales_count = order_items.aggregate(total=Sum('quantity'))['total']

    # Get all sold products
    sold_products = Product.objects.filter(id__in=order_items.values_list('product_id')).distinct()

    # Get the total sales for each sold product
    sales_by_product = order_items.values('product_id').annotate(total_sales=Sum('total_cost'))

    # Add the total sales to each sold product object
    for product in sold_products:
        try:
            product.total_sales = sales_by_product.get(product_id=product.id)['total_sales']
        except OrderItem.DoesNotExist:
            product.total_sales = 0

    context = {
        'sold_products': sold_products,
        'total_sales_count': total_sales_count
    }
    return render(request, 'sales_today.html', context)


def order_summary_data(request):
    # Get the order data
    orders = OrderPlaced.objects.all()
    order_count = orders.count()
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Group the orders by month
    orders_by_month = orders.annotate(month=TruncMonth('ordered_date')).values('month').annotate(count=Count('id')).order_by('month')
    labels = [month['month'].strftime('%B %Y') for month in orders_by_month]
    order_count_by_month = [month['count'] for month in orders_by_month]

    # Return the order data in JSON format
    data = {
        'labels': labels,
        'order_count': order_count_by_month,
        'total_sales': [total_sales for _ in order_count_by_month]
    }
    return JsonResponse(data)

#
# @csrf_exempt
# def sentiment_analysis(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#
#     # Call the `plot_sentiments()` method to generate the pie chart image
#     fig = product.plot_sentiments()
#     canvas = FigureCanvas(fig)
#     buf = io.BytesIO()
#     canvas.print_png(buf)
#     image_data = buf.getvalue()
#
#     context = {
#         'product': product,
#         'image_data': image_data,
#     }
#
#     return render(request, 'sentiment_analysis.html', context)

# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Product, Review
#
# def sentiment_analysis_chart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#
#     # Get the reviews for this product
#     reviews = product.review_set.all()
#
#     # Count the number of reviews in each sentiment category
#     sentiment_counts = {
#         'highly_positive': 0,
#         'positive': 0,
#         'neutral': 0,
#         'negative': 0,
#         'highly_negative': 0,
#     }
#     for review in reviews:
#         score = review.sentiment_score
#         if score >= 0.9:
#             sentiment_counts['highly_positive'] += 1
#         elif score >= 0.6:
#             sentiment_counts['positive'] += 1
#         elif score >= 0.4:
#             sentiment_counts['neutral'] += 1
#         elif score >= 0.1:
#             sentiment_counts['negative'] += 1
#         else:
#             sentiment_counts['highly_negative'] += 1
#
#     # Construct the data for the chart
#     chart_data = {
#         'labels': [
#             'Highly Positive',
#             'Positive',
#             'Neutral',
#             'Negative',
#             'Highly Negative',
#         ],
#         'data': [
#             sentiment_counts['highly_positive'],
#             sentiment_counts['positive'],
#             sentiment_counts['neutral'],
#             sentiment_counts['negative'],
#             sentiment_counts['highly_negative'],
#         ],
#         'backgroundColor': [
#             'rgba(54, 162, 235, 0.2)',
#             'rgba(75, 192, 192, 0.2)',
#             'rgba(255, 206, 86, 0.2)',
#             'rgba(255, 99, 132, 0.2)',
#             'rgba(255, 159, 64, 0.2)',
#         ],
#         'borderColor': [
#             'rgba(54, 162, 235, 1)',
#             'rgba(75, 192, 192, 1)',
#             'rgba(255, 206, 86, 1)',
#             'rgba(255,99,132,1)',
#             'rgba(255, 159, 64, 1)',
#         ],
#         'borderWidth': 1,
#     }
#
#     # Return the chart data as a JSON response
#     return JsonResponse(chart_data)


#
# @csrf_exempt
# def prebook(request):
#     if request.method == "POST":
#         # Get the form data
#         name = request.POST.get("name")
#         phone = request.POST.get("phone")
#         address = request.POST.get("address")
#         place = request.POST.get("place")
#         pincode = request.POST.get("pincode")
#         date = request.POST.get("date")
#         total_amount = request.POST.get("total_amount")
#
#         # Save the data in the model
#         booking = PreBooking(
#             user=request.user,
#             name=name,
#             phone=phone,
#             address=address,
#             place=place,
#             pincode=pincode,
#             date=date,
#             total_amount=total_amount
#         )
#         booking.save()
#         messages.success(request,'Payment Success')
#     return render(request,'prebooking.html')
