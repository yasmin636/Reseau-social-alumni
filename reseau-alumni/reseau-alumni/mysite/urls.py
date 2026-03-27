from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Bienvenue sur le Réseau Social Alumni 🎓")

urlpatterns = [
    path('', home),
]
