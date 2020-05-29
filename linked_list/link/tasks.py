from bs4 import BeautifulSoup
from celery import shared_task
from dateutil.parser import parse as dateparse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import transaction
from django.utils.timezone import now, is_aware, make_aware
import extruct
import logging
from mimetypes import guess_extension
import os
from PIL import Image
import requests
import shutil
from uuid import uuid4
from author.models import Author, AuthorSocial
from link.models import Link, LinkKeyword
from publisher.models import Publisher, PublisherSocial

_logger = logging.getLogger(__name__)


def _process_webpage(text, url, result):
    source = 'html'
    soup = BeautifulSoup(text, 'html5lib')
    result.append({
        'name': 'page.url',
        'value': url,
        'source': source,
    })
    if soup.title.string:
        result.append({
            'name': 'page.title',
            'value': soup.title.string,
            'source': source,
        })

    el = soup.find('meta', attrs={'name': 'description'})
    if el and el.get('content'):
        result.append({
            'name': 'page.description',
            'value': el.get('content'),
            'source': source,
        })

    el = soup.find('meta', attrs={'name': 'author'})
    if el and el.get('content'):
        result.append({
            'name': 'author.name',
            'value': el.get('content'),
            'source': source,
        })

    el = soup.find('meta', attrs={'name': 'keywords'})
    if el and el.get('content'):
        result.append({
            'name': 'page.keywords',
            'value': [x.strip() for x in el.get('content').split(',')],
            'source': source,
        })

def _process_jsonld(data, result):
    source = 'json-ld'
    for meta in data[source]:
        if meta['@type'] == 'Organization':
            logo = meta.get('logo')
            if logo and 'url' in logo:
                result.append({
                    'name': 'publisher.image.url',
                    'value': logo['url'],
                    'source': source,
                })
            if 'name' in meta:
                result.append({
                    'name': 'publisher.name',
                    'value': meta['name'],
                    'source': source,
                })
            if 'url' in meta:
                result.append({
                    'name': 'publisher.url',
                    'value': meta['url'],
                    'source': source,
                })
            if 'sameAs' in meta:
                result.append({
                    'name': 'publisher.social',
                    'value': meta['sameAs'],
                    'source': source,
                })

def _process_microdata(data, result):
    source = 'microdata'
    for meta in data[source]:
        if meta['type'] == 'http://schema.org/NewsArticle':
            news = meta.get('properties')
            if news and 'articleBody' in news:
                result.append({
                    'name': 'page.body.text',
                    'value': news['articleBody'],
                    'source': source,
                })
            if news and 'associatedMedia' in news and\
                    news['associatedMedia'].get('type')\
                    == 'http://schema.org/ImageObject':
                media = news['associatedMedia'].get('properties')
                if media and 'contentUrl' in media:
                    result.append({
                        'name': 'page.image.url',
                        'value': media['contentUrl'],
                        'source': source,
                    })
                if media and 'description' in media:
                    result.append({
                        'name': 'page.image.alt',
                        'value': media['description'],
                        'source': source,
                    })
                if media and 'url' in media:
                    result.append({
                        'name': 'page.image.url',
                        'value': media['url'],
                        'source': source,
                    })
            if news and 'author' in news:
                author = news['author'].get('properties')
                if author and 'name' in author:
                    result.append({
                        'name': 'author.name',
                        'value': author['name'],
                        'source': source,
                    })
                if author and 'sameAs' in author:
                    result.append({
                        'name': 'author.social',
                        'value': [author['sameAs']],
                        'source': source,
                    })
            if news and 'datePublished' in news:
                result.append({
                    'name': 'page.published_at',
                    'value': dateparse(news['datePublished']),
                    'source': source,
                })
            if news and 'description' in news:
                result.append({
                    'name': 'page.description',
                    'value': news['description'][0],
                    'source': source,
                })
            if news and 'headline' in news:
                result.append({
                    'name': 'page.title',
                    'value': news['headline'],
                    'source': source,
                })
            if news and 'mainEntityOfPage' in news:
                result.append({
                    'name': 'page.url',
                    'value': news['mainEntityOfPage'],
                    'source': source,
                })
            if news and 'publisher' in news and\
                    news['publisher'].get('type')\
                    == 'https://schema.org/Organization':
                publisher = news['publisher'].get('properties')
                if publisher and 'name' in publisher:
                    result.append({
                        'name': 'publisher.name',
                        'value': publisher['name'],
                        'source': source,
                    })
                if publisher and 'logo' in publisher and\
                        publisher['logo'].get('type')\
                        == 'https://schema.org/ImageObject':
                    media = publisher['logo'].get('properties')
                    if media and 'url' in media:
                        result.append({
                            'name': 'publisher.image.url',
                            'value': media['url'],
                            'source': source,
                        })

def _process_opengraph(data, result):
    source = 'opengraph'
    for meta in data[source]:
        if 'properties' not in meta:
            continue
        props = meta['properties']
        for prop in props:
            if prop[0] == 'og:url':
                result.append({
                    'name': 'page.url',
                    'value': prop[1],
                    'source': source,
                })
            elif prop[0] == 'article:author':
                result.append({
                    'name': 'author.social',
                    'value': [prop[1]],
                    'source': source,
                })
            elif prop[0] == 'og:description':
                result.append({
                    'name': 'page.description',
                    'value': prop[1],
                    'source': source,
                })
            elif prop[0] == 'og:image':
                result.append({
                    'name': 'page.image.url',
                    'value': prop[1],
                    'source': source,
                })
            elif prop[0] == 'article:publisher':
                result.append({
                    'name': 'publisher.social',
                    'value': [prop[1]],
                    'source': source,
                })
            elif prop[0] == 'article:published_time':
                result.append({
                    'name': 'page.published_at',
                    'value': dateparse(prop[1]),
                    'source': source,
                })
            elif prop[0] == 'og:title':
                result.append({
                    'name': 'page.title',
                    'value': prop[1],
                    'source': source,
                })
            elif prop[0] == 'article:tag':
                result.append({
                    'name': 'page.keywords',
                    'value': [x.strip() for x in prop[1].split(',')],
                    'source': source,
                })
            elif prop[0] == 'og:site_name':
                result.append({
                    'name': 'publisher.name',
                    'value': prop[1],
                    'source': source,
                })


@shared_task
def process_url(url):
    result = []
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()

    _process_webpage(response.text, url, result)

    data = extruct.extract(response.text, url)
    _process_jsonld(data, result)
    _process_microdata(data, result)
    #_process_microformat(data, result)
    _process_opengraph(data, result)
    #_process_rdfa(data, result)

    unique_meta = []
    non_unique_meta = []

    names = set(meta['name'] for meta in result)
    for name in names:
        value = None
        for meta in result:
            if not meta['name'] == name:
                continue
            if value is None:
                value = meta['value']
            elif meta['value'] != value:
                non_unique_meta.append(name)
                break
        else:
            unique_meta.append(name)

    return {
        'data': result,
        'conflicts': non_unique_meta,
    }


@shared_task
@transaction.atomic
def store_link_data(values):
    User = get_user_model()
    try:
        user = User.objects.get(pk=values['user.id'])
    except User.DoesNotExist:
        return

    date = None
    if 'page.published_at' in values:
        date = dateparse(values['page.published_at'])
        if not is_aware(date):
            date = make_aware(date)

    upload_dir = settings.FORM_DATA_UPLOAD_DIR

    page_image_path = None
    if 'page.image.url' in values:
        r = requests.get(values['page.image.url'], stream=True)
        if r.ok:
            page_image_path = os.path.join(upload_dir, uuid4().hex)
            with open(page_image_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    author_image_path = None
    if 'author.image.url' in values:
        r = requests.get(values['author.image.url'], stream=True)
        if r.ok:
            author_image_path = os.path.join(upload_dir, uuid4().hex)
            with open(author_image_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    publisher_image_path = None
    if 'publisher.image.url' in values:
        r = requests.get(values['publisher.image.url'], stream=True)
        if r.ok:
            publisher_image_path = os.path.join(upload_dir, uuid4().hex)
            with open(publisher_image_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    author = None
    if 'author.name' in values:
        try:
            author = Author.objects.get(user=user, name=values['author.name'])
            if date and author.updated_at < date:
                pass
        except Author.DoesNotExist:
            author = Author(
                    name=values['author.name'],
                    user=user,
                    updated_at=date or now())

            if author_image_path:
                im = Image.open(author_image_path)
                ext = guess_extension(Image.MIME[im.format])

                author.image_height = im.size[1]
                author.image_width = im.size[0]
                author.image.save(
                        os.path.basename(author_image_path) + ext,
                        File(open(author_image_path, 'rb')))

            author.save()

            for social_url in values.get('author.social', []):
                social = AuthorSocial(url=social_url, entity=author, user=user)
                social.save()

    publisher = None
    if 'publisher.name' in values:
        try:
            publisher = Publisher.objects.get(user=user,
                    name=values['publisher.name'])
            if date and publisher.updated_at < date:
                pass
        except Publisher.DoesNotExist:
            publisher = Publisher(
                    name=values['publisher.name'],
                    user=user,
                    updated_at=date or now())

            if publisher_image_path:
                im = Image.open(publisher_image_path)
                ext = guess_extension(Image.MIME[im.format])

                publisher.image_height = im.size[1]
                publisher.image_width = im.size[0]
                publisher.image.save(
                        os.path.basename(publisher_image_path) + ext,
                        File(open(publisher_image_path, 'rb')))

            publisher.save()

            for social_url in values.get('publisher.social', []):
                social = PublisherSocial(url=social_url, entity=publisher,
                        user=user)
                social.save()

    link = Link(
            url=values.get('page.url'),
            title=values.get('page.title'),
            description=values.get('page.description'),
            text=values.get('page.body.text'),
            html=values.get('page.body.html'),
            author=author,
            publisher=publisher,
            user=user,
            published_at=date)

    if page_image_path:
        im = Image.open(page_image_path)
        ext = guess_extension(Image.MIME[im.format])

        link.image_height = im.size[1]
        link.image_width = im.size[0]
        link.image.save(
                os.path.basename(page_image_path) + ext,
                File(open(page_image_path, 'rb')))

    link.save()

    if 'page.keywords' in values:
        for name in values['page.keywords']:
            keyword, created = LinkKeyword.objects.get_or_create(name=name)
            link.keywords.add(keyword)

    return link.id
