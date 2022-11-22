from django.urls import path
from . import views

urlpatterns = [
    path('smm/', views.smm, name="smm"),
    path('success/', views.success, name='success'),
]
