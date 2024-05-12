from django.shortcuts import render
from .models import Anketa,Employer

def index(request):
    main = Anketa.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная страница','main': main})

def about(request):
    vacan = Employer.objects.all()
    return render(request, 'main/about.html', {'title': 'Про нас','vacan': vacan})