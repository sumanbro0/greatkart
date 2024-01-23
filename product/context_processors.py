from cart.models import Cart


def add_search_query_to_context(request):
    query = request.GET.get('query', '')
    cart=Cart.objects.get(user=request.user)
    cart_count=0
    if cart:
        cart_count=cart.items.all().count()
    
    return {'search_query': query,"cart_count":cart_count} # used in base.html to display the search query