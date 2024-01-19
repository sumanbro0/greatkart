def add_search_query_to_context(request):
    query = request.GET.get('query', '')
    return {'search_query': query} # used in base.html to display the search query