from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
# from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User,auth
from .forms import UserRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import View
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate
import razorpay
from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist
import math,random


# Create your views here.
def index(request):
    if 'search' in request.GET:
        search = request.GET['search']
        product = Product.objects.filter(name__icontains=search)
    else:
        product = Product.objects.all()
    categories = Category.objects.all()
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

def review(request):
    if request.method == "POST":
        usr = request.user
        title = request.POST.get('title')
        review = request.POST.get('review')
        image = request.FILES.get('wimg')
        user = Reviews(title=title,review=review,image=image,user=usr)
        user.save()
        messages.info(request, 'Your review has been successfully send..!!')
        return redirect('review')
    return render(request, 'mailbox-compose.html')



#
# class ProfileView(View):
#     def get(self, request):
#         form = CustomerProfileForm()
#         return render(request, 'profile.html', {'form':form})
#
#     def post(self, request):
#         form = CustomerProfileForm(request.POST)
#         if form.is_valid():
#             usr = request.user
#             name = form.cleaned_data['name']
#             phone=  form.cleaned_data['phone']
#             address = form.cleaned_data['address']
#             city = form.cleaned_data['city']
#             state = form.cleaned_data['state']
#             zipcode = form.cleaned_data['zipcode']
#             reg = Customer(user=usr,name=name,phone=phone, address=address, city=city, state=state, zipcode=zipcode)
#             reg.save()
#             return redirect('address')
#         return render(request, 'profile.html',{'form':form})




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


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    #print(product_id)
    product = Product.objects.get(id=product_id)
    if Cart.objects.filter(user=user, product=product).exists():
        c_item1 = Cart.objects.get(user=user, product=product)
        print(c_item1.quantity)
        c_item1.quantity = c_item1.quantity + 1
        c_item1.save()
        return redirect('index')
    else:
        Cart(user=user, product=product).save()
        messages.success(request, "Added to cart Successfully")
    return redirect('index')
    # Cart(user=user,product=product).save()
    # # return redirect('/show_cart')
    # messages.success(request,'product added successfuly!!')
    # return redirect('index')


def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('id')
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                subtotal = (p.quantity * p.product.selling_price)
                amount += subtotal
            total_amount = amount + shipping_amount
            context = {'cart':cart, 'total_amount':total_amount, 'amount':amount}
            return render(request, 'addtocart.html', context)
        else:
            return render(request, 'emptycart.html')
    #     if request.method == 'POST':
    #         coupon = request.POST.get('coupon')
    #         coupon_obj = Voucher.objects.filter(coupon_code = coupon)
    #         if not coupon_obj.exist():
    #             messages.warning(request,'Invalid Coupon')
    #             print('invalis')
    #             return HttpResponseRedirect(request.META.get('HTTP_REFER'))
    #         if cart.coupon:
    #             print('alrdy')
    #             messages.warning(request, 'Coupon alrdy exists')
    #             return HttpResponseRedirect(request.META.get('HTTP_REFER'))
    #         cart.coupon = coupon_obj[0]
    #         cart.save()
    #         messages.success(request,'coupon applied')
    #         return HttpResponseRedirect(request.META.get('HTTP_REFER'))
    #
    #
    # return render(request,'addtocart.html')





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

#
# def de_cart(request):
#     user = request.user
#     product_id = request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     product.delete()
#     return redirect('/show_cart/')

# def remove_ad(request):
#     user = request.user
#     address_id = request.GET.get('add_id')
#     # print(product_id)
#     product = Profile.objects.get(id=address_id)
#     Profile(user=user, id=product).delete()
#     return redirect('/address')
def remove_ad(request, id):
    user = request.user
    cart = Profile.objects.filter(user_id=user)
    if cart.exists():
        Profile.objects.get(id=id).delete()
        # messages.warning(request, "This address is removed!!!")
        # messages.info(request, "You don't have an active order")
        return redirect('/address')


class checkout(View):
    def get(self, request):
      user = request.user
      address = Profile.objects.filter(user=request.user)
      cart = Cart.objects.filter(user=request.user)
      amount = 0
      shipping_amount = 70
      cart_product = [p for p in Cart.objects.all() if p.user == request.user]
      if cart_product:
         for p in cart_product:
            subtotal = p.quantity * p.product.selling_price
            amount = amount + subtotal
         totalamount = amount + shipping_amount
         print(totalamount)
         razoramount =  totalamount * 100
         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
         data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_11"}
         payment_response = client.order.create(data=data)
         print(payment_response)

         order_id = payment_response['id']
         request.session['order_id'] = order_id
         order_status = payment_response['status']
         if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status= order_status
            )
            payment.save()
         return render(request,'checkout.html',locals())
         # return render(request, 'checkout.html',
         #          {'address': address, 'cart': cart,'amount': razoramount, 'subtotal': subtotal, 'total_amount': totalamount,
         #           'amount': amount, 'shipping_amount': shipping_amount})

def payment_done(request):
    order_id= request.session['order_id']
    payment_id = request.GET.get('payment_id')
    print(payment_id)
    cust_id = request.GET.get('cust_id')
    user = request.user
    payment= Payment.objects.get(razorpay_order_id=order_id)
    payment.paid= True
    payment.razorpay_payment_id = payment_id
    payment.save()
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect('order')
def order(request):
    order_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request,'order.html',locals())


def de_cart(request, id):
    user = request.user
    cart = Cart.objects.filter(user_id=user)
    if cart.exists():
        Cart.objects.get(id=id).delete()
        messages.warning(request, "This product is removed form your cart")
        # messages.info(request, "You don't have an active order")
        return redirect('show_cart')



