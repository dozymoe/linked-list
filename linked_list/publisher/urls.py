from django.urls import path

from . import views

app_name = 'publisher'
urlpatterns = [
    path('', views.index, name='index'),
]
