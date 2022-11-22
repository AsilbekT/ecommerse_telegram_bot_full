from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('orders/', views.orders),
    path('statistics/', views.statistics)
]
