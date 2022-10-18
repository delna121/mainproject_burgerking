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
    data = {'product':product, 'categories':categories, 'result':obj}
    return render(request, 'index.html', data)


def showcategory(request, cid):
    categories = Category.objects.all()
    obj = Deals.objects.all()
    cats = Category.objects.get(pk=cid)
    product = Product.objects.filter(cat=cats)
    data = {
        'categories':categories,
        'result': obj,
        'product':product
    }
    return render(request, 'index.html', data)


    # if request.method == 'GET':
    #     category_id = request.GET.get('category_id')
    #     #print(category_id)
    #     product = Product.objects.filter(Q(cat=category_id)).values()
    #     # for p in product:
    #     #     #product = p.values()
    #     product=json.dumps(list(product.values()))
    #     print(product)
    #         #print(product)
    #     data ={
    #         'product':product,
    #     }
    #     print(data)
    #     return JsonResponse(data)
    #     #print(data)    

    

        



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
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name, address=address, city=city, state=state, zipcode=zipcode)
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

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_to_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    try:
        cart=Cart_details.objects.get(cart_id=_cart_id(request))
    except Cart_details.DoesNotExist:
        cart=Cart_details.objects.create(
            cart_id=_cart_id(request)

        )
        cart.save(),
    try:
        cart_item=CartItem.Objects.get(product=product,cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart:cart_detail')




    # user = request.user
    # product_id = request.GET.get('prod_id')
    # #print(product_id)
    # product = Product.objects.get(id=product_id)
    # CartItem(user=user,product=product).save()
    # return redirect('/show_cart')

def show_cart(request,total=0,counter=0,cart_items=None):
    try:
        cart=Cart_details.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.selling_price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass
    return render(request,'cart.html',dict(cart_item=cart_items,total=total,counter=counter))

    # if request.user.is_authenticated:
    #     user = request.user
    #     cart = CartItem.objects.filter(user=user).order_by('-id')
    #
    #     amount = 0.0
    #     shipping_amount = 70.0
    #     total_amount = 0.0
    #     cart_product = [p for p in CartItem.objects.all() if p.user == user]
    #     #print(cart_product)
    #     if cart_product:
    #         for p in cart_product:
    #             subtotal = (p.quantity * p.product.selling_price)
    #             amount += subtotal
    #             total_amount = amount + shipping_amount
    #         return render(request, 'addtocart.html', {'cart':cart, 'total_amount':total_amount, 'amount':amount})
    #     else:
    #         return render(request, 'emptycart.html')



def address(request):
    address = Customer.objects.filter(user=request.user)
    return render(request, 'address.html', {'address':address})


