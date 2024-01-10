from django.urls import path
from . import views

app_name ='App'

urlpatterns = [
    path('', views.home, name="home"),
    path('search', views.search, name='search'),
    path("contact", views.contact, name="contact"),
]
