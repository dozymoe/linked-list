"""linked_list URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    #path('account/', include('django.contrib.auth.urls')),
    path('links/', include('link.urls', namespace='links')),
    path('authors/', include('author.urls', namespace='authors')),
    path('publishers/', include('publisher.urls', namespace='publishers')),
    path('', views.index, name='home'),
]
