from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    #if request.method == 'POST':
    #else:
    return render(request, 'register.html')
