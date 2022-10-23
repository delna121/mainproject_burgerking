from django.shortcuts import render, redirect
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import View
from django.db.models import Q
from django.http import JsonResponse
import json

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
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Account Register Successfully')
            form.save()

    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form':form})




class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'profile.html', {'form':form})
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            phone=form.cleaned_data['phone']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name,phone=phone, address=address, city=city, state=state, zipcode=zipcode)
            reg.save()
        return render(request, 'profile.html',{'form':form})
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
    user= request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    CartItem(user=user, product=product).save()
    return redirect('/show_cart')

def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = CartItem.objects.filter(user=user).order_by('-id')

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in CartItem.objects.all() if p.user == user]
        # print(cart_product)
        if cart_product:
            for p in cart_product:
                subtotal = (p.quantity * p.product.selling_price)
                amount += subtotal
                total_amount = amount + shipping_amount
            return render(request, 'cart.html', {'cart': cart, 'total_amount': total_amount, 'amount': amount})
        else:
            return render(request, 'emptycart.html')






