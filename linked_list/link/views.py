from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
import logging
from django_redis import get_redis_connection
import json
from uuid import uuid4
from .forms import CreateForm, CreateChooseForm, LINK_FIELDS
from .models import Link
from .tasks import process_url, store_link_data

_logger = logging.getLogger(__name__)


@login_required
def index(request):
    return HttpResponse("Links index underconstruction.")


@login_required
def create(request):
    pcache = get_redis_connection('persistent')
    keyname = 'formdata:%s:' % request.user.id

    form_id = request.GET.get('form_id')
    if not form_id:
        if request.method != 'POST':
            return render(request, 'link/create.html', {'form': CreateForm()})

        form = CreateForm(request.POST)
        if not form.is_valid():
            return render(request, 'link/create.html', {'form': form})

        result = process_url.delay(form.cleaned_data['url'])
        data = result.get(timeout=180, propagate=False)
        if not data or isinstance(data, Exception):
            form.add_error('url', "Unable to process the webpage, contact "
                    "website administrator.")
            return render(request, 'link/create.html', {'form': form})

        data['values'] = {'user.id': request.user.id}
        for item in data['data']:
            if item['name'] in data['conflicts']:
                continue
            data['values'][item['name']] = item['value']

        if not data['conflicts']:
            return _save_link_data(request, data['values'])

        # store form data
        form_id = uuid4().hex
        keys = pcache.keys(keyname + '*')
        if keys:
            pcache.delete(*keys)
        keyname += form_id
        pcache.setex(keyname, timedelta(days=2), json.dumps(data))

        return HttpResponseRedirect('%s?%s' % (reverse('links:create'),
                urlencode({'form_id': form_id})))

    keyname += form_id
    data = pcache.get(keyname)
    if not data:
        raise Http404("The form has expired.")
    data = json.loads(data)

    if request.method == 'POST':
        form = CreateChooseForm(request.POST)
        if form.is_valid():
            _logger.error(form.cleaned_data)
            try:
                name = form.cleaned_data['name']
                value = form.cleaned_data['value']
                data['values'][name] = value
                data['conflicts'].remove(name)
                pcache.setex(keyname, timedelta(days=2), json.dumps(data))
            except:
                pass

    if data['conflicts']:
        name = data['conflicts'][0]
        values = [item for item in data['data'] if item['name'] == name]
        return render(
                request,
                'link/create_choose.html',
                {
                    'form': CreateChooseForm(initial={'name': name}),
                    'label': dict(LINK_FIELDS)[name],
                    'type': 'image' if name.endswith('image.url') else None,
                    'values': values,
                })

    result = store_link_data.delay(data['values'])
    data = result.get(timeout=360, propagate=False)
    return HttpResponseRedirect(reverse('home'))
