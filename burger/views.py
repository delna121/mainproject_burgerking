from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
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
    data = {'product':product, 'categories':categories, 'result': obj}
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
            print(2)
            auth.login(request,user)
            #save email in session
            request.session['username'] = username
            return redirect('index')
        else:
            print(3)
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





class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'profile.html', {'form':form})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            phone=  form.cleaned_data['phone']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name,phone=phone, address=address, city=city, state=state, zipcode=zipcode)
            reg.save()
            return redirect('address')
        return render(request, 'profile.html',{'form':form})




@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

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
    address = Customer.objects.filter(user=request.user)
    return render(request, 'address.html', {'address':address})


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    #print(product_id)
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/show_cart')

def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('-id')

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        #print(cart_product)
        if cart_product:
            for p in cart_product:
                subtotal = (p.quantity * p.product.selling_price)
                amount += subtotal
                total_amount = amount + shipping_amount
            return render(request, 'addtocart.html', {'cart':cart, 'total_amount':total_amount, 'amount':amount})
        else:
            return render(request, 'emptycart.html')


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

        data = {
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


def checkout(request):
    address = Customer.objects.filter(user=request.user)
    cart = Cart.objects.filter(user=request.user)

    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            subtotal = (p.quantity * p.product.selling_price)
            amount += subtotal
            total_amount = amount + shipping_amount
    return render(request, 'checkout.html',
                  {'address': address, 'cart': cart, 'subtotal': subtotal, 'total_amount': total_amount,
                   'amount': amount, 'shipping_amount': shipping_amount})



# "def change(request):
#     return render(request,'changepassword.html')"

# def logout(request):
#     if 'user' in request.session:
#         request.session.flush()
#     return redirect('login')