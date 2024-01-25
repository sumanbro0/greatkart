from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage

from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from profiles.models import Address
from xhtml2pdf import pisa

from .models import Cart, CartItem, Order
from product.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required


import requests
import json
from django.urls import reverse

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
    

@login_required
def clear_cart(request):
    pass

@login_required
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

@login_required
def checkout(request):
    addresses=Address.objects.filter(profile__user=request.user)
    cart=Cart.objects.prefetch_related("items__variant_product","items__product").get(user=request.user)
    if not cart.items.exists():
        messages.error(request,"Your cart is empty.")
        return redirect("cart")
    return render(request,"cart/checkout.html",{"addresses":addresses,"cart":cart})


@login_required
def initiate_khalti_payment(request,order):
    

    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    return_url = request.build_absolute_uri(reverse("order_complete"))
    website_url = request.build_absolute_uri(reverse("home"))
    payload = json.dumps({
        "return_url":return_url ,
        "website_url": website_url,
        "amount": order.total * 100,
        "purchase_order_id": order.id,
        "purchase_order_name": "order_"+str(order.id),
        "customer_info": {
            "name": order.user.profile.full_name,
            "email": order.user.email   
            }
    })
    headers = {
        'Authorization': 'key live_secret_key_68791341fdd94846a146f0457ff7b455',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    return json.loads(response.text)

@login_required
def place_order(request):
    cart=Cart.objects.prefetch_related("items__variant_product","items__product").get(user=request.user)
    if not cart.items.exists():
        messages.error(request,"Your cart is empty.")
        return redirect("cart")

    address_id=request.GET.get("address_id",None)
    payment_method=request.GET.get("payment",None)
    if not address_id or not payment_method:
        messages.error(request,"Please select a valid address and payment method.")
        return redirect("checkout")
    
    address=Address.objects.get(id=address_id,profile__user=request.user)
    if payment_method=="pod":
        o=cart.convert_to_order(address)
        messages.success(request,"Order placed successfully.")
        return render(request,"cart/order_complete.html",{"order":o,"pod":True})
    
    if payment_method=="khalti":
        o=cart.convert_to_order(address)
        res=initiate_khalti_payment(request,o)
        if res.get("pidx",None):
            o.payment_id=res['pidx']
            o.is_paid=True
            o.save()
            return HttpResponse('<script>window.location.href="{}";</script>'.format(res['payment_url']))
        else:
            messages.error(request,"Error occured while placing order. Please try again.")
            return redirect("checkout")
    
    return render(request,"cart/order_complete.html",{"cart":cart})

@login_required
def order_complete(request):
    order_id=request.GET.get("purchase_order_id",None)
    o=Order.objects.select_related("user","shipping_address","coupon").get(id=order_id,user=request.user)
    return render(request,"cart/order_complete.html",{"order":o})





@login_required
def download_invoice(request, order_id):
    order = Order.objects.select_related("user","shipping_address","coupon").get(id=order_id,user=request.user)
    if order.items.all():
        template = get_template('cart/invoice.html')

        logo_url = request.build_absolute_uri(staticfiles_storage.url('images/logo.png'))
        html_string = template.render({'order': order, 'logo_url': logo_url})

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("ISO-8859-1")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
            return response
        else:
            return HttpResponse('Error Rendering PDF', status=400)
    else:
        messages.error(request, "You cannot download an empty invoice.")
        return redirect('me')

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, 'Order deleted successfully.')
    return redirect('orders')