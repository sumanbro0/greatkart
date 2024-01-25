from cart.models import Cart


def add_search_query_to_context(request):
    query = request.GET.get('query', '')
    cart=None
    try:
        if request.user and request.user.is_authenticated and not (request.user.is_superuser or request.user.is_staff):
            cart=Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        pass
    cart_count=0
    if cart:
        cart_count=cart.items.all().count()
    
    return {'search_query': query,"cart_count":cart_count} # used in base.html to display the search query