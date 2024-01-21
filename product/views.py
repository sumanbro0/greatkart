from urllib.parse import urlencode
from django.shortcuts import render
from .models import Category, Color, Product, Size
from django.db.models import Avg
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.
def index(request):
    products = Product.objects.prefetch_related("images").annotate(average_rating=Avg('reviews__rating')).order_by('-average_rating')[:5]
    query = request.GET.get('query')
    if query:
        products_list = Product.objects.prefetch_related("images").filter(Q(name__icontains=query) | Q(desc__icontains=query))
        return render(request, 'index.html',{"products":products_list, "query":query})

    return render(request, 'index.html',{"products":products})

def search_suggestions(request):
    query = request.GET.get('query', '')
    items = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query))[:5]
    return render(request, 'search_suggestions.html', {'items': items})

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
    print(base_query_string)
    context = {
        'products': products,
        'categories': categories,
        'sizes': sizes,
        'price_options': price_options,
        'n': n,
        'query_string': base_query_string,  # Add this line
    }
    referrer = request.META.get('HTTP_REFERER', '')

    if request.htmx and "store" in referrer and base_query_string:
        return render(request, 'products_list.html', context)

    return render(request, 'store.html', context)


def product_detail(request, id):
    print("new request ************")
    product = Product.objects.prefetch_related("images","variants","reviews").get(id=id)
    size_names=product.variants.values_list('sizes__name', flat=True).distinct()
    color_names=product.variants.values_list('color__name', flat=True).distinct()
    sizes=Size.objects.filter(name__in=size_names)
    colors=Color.objects.filter(name__in=color_names)
    size_id=request.GET.get('size')
    color_id=request.GET.get('color')
    variant=None
    if size_id and color_id:
        variant=product.variants.filter(sizes__id=size_id,color__id=color_id).first()
    elif size_id:
        variant=product.variants.filter(sizes__id=size_id).first()
    elif color_id:
        variant=product.variants.filter(color__id=color_id).first()
        
        
    price=product.get_final_price(variant)
    in_stock=product.is_in_stock(variant)
    if request.htmx and variant:
        return render(request, 'detail_content.html', {"product":product,"price":price,"in_stock":in_stock})
    return render(request, 'product_detail.html', {"product":product,"sizes":sizes,"colors":colors,"price":price,"in_stock":in_stock})