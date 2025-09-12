from django.shortcuts import render

def home(request):
    return render(request, 'reports/home.html')
