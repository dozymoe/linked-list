from django.contrib.auth import authenticate, login, logout
#from django.shortcuts import redirect, render

def login_page(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # redirect
    else:
        # return error messages
        pass


def logout_page(request):
    logout(request)
    # redirect to login page
