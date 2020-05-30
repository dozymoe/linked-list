from django.http import HttpResponse
#from django.shortcuts import render

def index(request):
    return HttpResponse("Hello, world. You are at the publishers index.")
