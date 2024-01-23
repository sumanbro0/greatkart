from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Cart, CartItem
from product.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
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
        messages.success(request, "Product added to cart successfully.")
    except Exception as e:
        messages.error(request, "This product is already in your cart.")
        return redirect(url+ query)
    return redirect(url+ query)


@login_required
def remove_from_cart(request,id):
    variant_id = request.GET.get('id',None)
    color=request.GET.get('color',"")
    size=request.GET.get('size',"")

    query="?color="+color+"&size="+size
    base_url=reverse('product',args=[id])
    referrer=request.META.get('HTTP_REFERER','')
    
    if "cart" in referrer:
        base_url=referrer
        query=""


    try:
        item=CartItem.objects.filter(product__id=id, cart__user=request.user).first()
    except CartItem.DoesNotExist:
        messages.error(request, "The item does not exist in your cart.")
        return redirect(base_url+query)
    
    if not item.variant_product:
        item.delete()
        messages.success(request, "Product variant removed from cart successfully.")
        return redirect(base_url)

    if not variant_id:
        messages.success(request, "Please select a size and color for this product.")
        return redirect(base_url+query)
    
    try:
        if variant_id and item.variant_product.id == int(variant_id):
            item.delete()
            messages.success(request, "Product variant removed from cart successfully.")

        else:
            messages.error(request, "The selected variant does not exist in your cart.")
        return redirect(base_url+query)


    except Exception as e:
        print(e)

    return redirect(base_url+query)
    


def clear_cart(request):
    pass

def cart(request):
    id=request.GET.get('cart_item_id',None)
    q=request.GET.get('quantity',None)
    if id and q:            
        try:
            item=CartItem.objects.get(id=id,cart__user=request.user)
            item.quantity=int(q) if int(q) > 0 else 1
            item.save()
        except Exception as e:
            print(e)
            messages.error(request,"The item does not exist in your cart.")
            
    cart=Cart.objects.prefetch_related("items__variant_product","items__product").get(user=request.user)
    
    context={"cart":cart}
    return render(request,"cart/cart.html",context) 

