from django.urls import path
from . import views

app_name = 'link'
urlpatterns = [
    path('add', views.create, name='create'),
    path('', views.index, name='index'),
]
