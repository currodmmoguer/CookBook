from django.core.paginator import Paginator

def paginator(request, lista, num=10):
    paginator = Paginator(lista, num)
    num_pagina = request.GET.get('page')
    obj_pagina = paginator.get_page(num_pagina)
    return obj_pagina