from django.core.paginator import Paginator
from django.shortcuts import render
from link.forms import CreateForm
from link.models import Link

def index(request):
    objects = Link.objects.order_by('-published_at')
    pagination = Paginator(objects, 15)
    page = pagination.get_page(request.GET.get('page'))

    if not request.user.is_authenticated:
        return render(request, 'website/home-anon.html', {})

    return render(
            request,
            'website/home.html',
            {
                'pager': page,
                'create_form': CreateForm(),
            })
