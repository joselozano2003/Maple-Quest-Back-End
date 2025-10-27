from django.urls import path
from django.http import HttpResponse
from . import views

def home(request):
    return HttpResponse("OK — MapleQuest is running!", status=200)

urlpatterns = [
    path('', home, name='home'),  # Root endpoint for "/"
]

urlpatterns = [
    path('', home, name='home'),  # Root endpoint for "/"
    path('health/', views.health_check, name='health_check'),
]