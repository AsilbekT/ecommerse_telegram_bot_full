from django.urls import path, include
from . import views 

urlpatterns = [
    path('get_total_amount_by_days/', views.get_total_amount_by_days, name="get_total_amount_by_days")
]