from django.shortcuts import render,redirect
from burger.models import Product
from . models import Carts,CartItems
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(requst,product_id):
    product=Product.objects.get(id=product_id)
    try:
        cart=Carts.objects.get(cart_id=_cart_id(requst))
    except Carts.DoesNotExist:
        cart=Carts.objects.create(
            cart_id=_cart_id(requst)
        )
        cart.save(),
    try:
        cart_item=CartItems.objects.get(product=product,cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    except CartItems.DoesNotExist:
        cart_item=CartItems.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()
    return redirect('cart:cart_detail')
def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart=Carts.objects.get(cart_id=_cart_id(request))
        cart_items=CartItems.objects.filter(cart=cart)
        for cart_i in cart_items:
            total += (cart_i.product.selling_price * cart_i.quantity)
            counter += cart_i.quantity
    except ObjectDoesNotExist:
        pass
    return render(request,'cart.html',dict(cart_items=cart_items,total=total,counter=counter))
