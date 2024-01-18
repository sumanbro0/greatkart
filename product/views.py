from django.shortcuts import render, get_object_or_404
from .models import Product
from django.db.models import Q

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    category = request.GET.get('category')
    if category:
        products = products.filter(category__icontains=category)
    price = request.GET.get('price')
    if price:
        products = products.filter(price__lte=price)
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product-detail.html', {'product': product})