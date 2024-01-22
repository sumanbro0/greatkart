from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Cart, CartItem
from product.models import Product
from django.contrib import messages

# Create your views here.

def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    url = reverse('product', args=[id])
    variant_id = request.GET.get('id')
    color = request.GET.get('color',"")
    size=request.GET.get('size',"")
    query="?color="+color+"&size="+size

    if not product.variants.exists():
        if not product.is_in_stock():
            messages.error(request, "Sorry, this product is currently out of stock.")
            return redirect(url)

        try:
            CartItem.objects.create(cart=cart, product=product)
            messages.success(request, "Product added to cart successfully.")
            return redirect(url)
        except Exception as e:
            messages.error(request, "This product is already in your cart.")
            return redirect(url)

    if not variant_id:
        messages.error(request, "Please select a size and color for this product.")
        return redirect(url+ query)

    try:
        variant = product.variants.get(id=variant_id)
    except Product.DoesNotExist:
        messages.error(request, "The selected variant does not exist.")
        return redirect(url + query)

    if not product.is_in_stock(variant):
        messages.error(request, "Sorry, the selected variant is currently out of stock.")
        return redirect(url + query)

    try:
        CartItem.objects.create(cart=cart, product=product, variant_product=variant)
        messages.success(request, "Product variant added to cart successfully.")
    except Exception as e:
        messages.error(request, "This variant is already in your cart.")
        return redirect(url+ query)
    return redirect(url+ query)

def remove_from_cart(request,id):
    pass


def clear_cart(request):
    pass

def cart(request):
    cart=Cart.objects.get(user=request.user)
    context={"cart":cart}
    return render(request,"cart/cart.html",context) 

