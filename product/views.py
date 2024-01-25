from urllib.parse import urlencode
from django.shortcuts import redirect, render

from cart.models import Cart
from .models import Category, Color, Product, Review, Size
from django.db.models import Avg
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def index(request):
    products = Product.objects.prefetch_related("images").annotate(average_rating=Avg('reviews__rating')).order_by('-average_rating')[:5]  
    return render(request, 'product/index.html',{"products":products})

def search_suggestions(request):
    query = request.GET.get('query', '')
    items = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query))[:5]
    return render(request, 'product/search_suggestions.html', {'items': items})

def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step

def store(request):
    category_ids = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    size_ids = request.GET.getlist('size')
    query=request.GET.get('query')
    
    products_list = Product.objects.all()
    cart_ids=Cart.objects.filter(user=request.user).values_list('items__product__id',flat=True)

    if category_ids:
        products_list = products_list.filter(category__id__in=category_ids)
    if min_price:
        products_list = products_list.filter(base_price__gte=min_price)
    if max_price:
        products_list = products_list.filter(base_price__lte=max_price)
    if size_ids:
        products_list = products_list.filter(variants__sizes__id__in=size_ids)
    if query:
        products_list = products_list.filter(Q(name__icontains=query) | Q(desc__icontains=query))
    
    product_ids = products_list.values_list('id', flat=True).distinct()

    products_list = Product.objects.filter(id__in=product_ids)
    paginator = Paginator(products_list, 1)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    n = products_list.count()

    categories = Category.objects.all()
    sizes = Size.objects.all()
    ma=max(Product.objects.all().values_list('base_price', flat=True))
    mi=min(Product.objects.all().values_list('base_price', flat=True))
    step=10.0
    price_options = list(frange(mi, ma + step, step))
    query_params = request.GET.copy()

    query_params.pop('page', None)

    base_query_string = query_params.urlencode()
    context = {
        'products': products,
        'categories': categories,
        'sizes': sizes,
        'price_options': price_options,
        'n': n,
        'query_string': base_query_string,  # Add this line
        'cart_ids':cart_ids,
    }
    referrer = request.META.get('HTTP_REFERER', '')

    if request.htmx and "store" in referrer:
        return render(request, 'product/products_list.html', context)

    return render(request, 'product/store.html', context)


def product_detail(request, id):
    product = Product.objects.prefetch_related("images","variants",'variants__sizes', 'variants__color',"reviews__user").get(id=id)
    cart_ids=Cart.objects.filter(user=request.user).values_list('items__product__id',flat=True)
    variant_ids = Cart.objects.filter(user=request.user).values_list('items__variant_product__id', flat=True)   

    size_names=product.variants.values_list('sizes__name', flat=True).distinct()
    color_names=product.variants.values_list('color__name', flat=True).distinct()
    sizes=Size.objects.filter(name__in=size_names)
    colors=Color.objects.filter(name__in=color_names)
    size_id=request.GET.get('size')
    color_id=request.GET.get('color')
    
    variant=None
    if colors and sizes:
        if size_id and color_id:
            variant=product.variants.filter(sizes__id=size_id,color__id=color_id).first()
    else:
        if size_id:
            variant=product.variants.filter(sizes__id=size_id).first()
        elif color_id:
            variant=product.variants.filter(color__id=color_id).first()
    price=product.get_final_price(variant)
    in_stock=product.is_in_stock(variant)
    review = product.reviews.filter(user=request.user)
    already_reviewed = review.exists()
    context={"product":product,"sizes":sizes,"colors":colors,"price":price,"in_stock":in_stock,"cart_ids":cart_ids,"variant_ids":variant_ids,"already_reviewed":already_reviewed,"review":review.first()}


    if variant:
        context['variant'] = variant.id

    return render(request, 'product/product_detail.html', context)

@login_required
def add_review(request, id):
    product = Product.objects.get(id=id)
    already_reviewed = product.reviews.filter(user=request.user).exists()
    review=None
    if request.method == "POST":
        if already_reviewed:
            messages.error(request, "You have already reviewed this product")
        else:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            try:
                review=Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
                already_reviewed=True
                messages.success(request, "Your review has been added")
            except Exception as e:
                print(e)
                messages.error(request, "Error adding review")

    return render(request, 'product/reviews.html', {"product": product, "already_reviewed": already_reviewed,"review":review})

@login_required
def update_review(request, id):
    product = Product.objects.get(id=id)
    review = product.reviews.filter(user=request.user).first()

    if request.method == "POST":
        if not review:
            messages.error(request, "No review to update")
        else:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            try:
                review.rating = rating
                review.comment = comment
                review.save()
                messages.success(request, "Your review has been updated")
            except Exception as e:
                print(e)
                messages.error(request, "Error updating review")

    return render(request, 'product/reviews.html', {"product": product, "review": review, "already_reviewed": True})

@login_required
def delete_review(request, id):
    review = Review.objects.get(id=id, user=request.user)
    review.delete()
    messages.success(request, "Your review has been deleted")
    return render(request,'product/reviews.html',{"product":review.product})