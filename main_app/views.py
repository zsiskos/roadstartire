from django.shortcuts import render

# Create your views here.

def home(req):
  return render(req, 'home.html')

def signup(req):
  return render(req, 'signup.html')