from urllib.parse import urlencode
from django.shortcuts import render
from .models import Category, Product, Size
from django.db.models import Avg
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    popular_products = Product.objects.prefetch_related("images").annotate(average_rating=Avg('reviews__rating')).order_by('-average_rating')[:5]
    return render(request, 'index.html',{"products":popular_products})


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

    products_list = Product.objects.all()

    if category_ids:
        products_list = products_list.filter(category__id__in=category_ids)
    if min_price:
        products_list = products_list.filter(base_price__gte=min_price)
    if max_price:
        products_list = products_list.filter(base_price__lte=max_price)
    if size_ids:
        products_list = products_list.filter(variants__sizes__id__in=size_ids)

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

    base_query_string = urlencode(query_params)

    context = {
        'products': products,
        'categories': categories,
        'sizes': sizes,
        'price_options': price_options,
        'n': n,
        'query_string': base_query_string,  # Add this line
    }
    if request.htmx:
        return render(request, 'products_list.html', context)
    return render(request, 'store.html', context)