from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # We call it 'index' as it's the main page
]