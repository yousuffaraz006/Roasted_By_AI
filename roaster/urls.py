from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('roast/', views.upload_and_roast, name='upload_and_roast'),
]