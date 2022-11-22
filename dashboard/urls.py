from django.urls import path, include
from . import views 

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('statistics/', views.statistics, name="statistics"),
    path('dashboard/mahsuloatlar_statistikasi/', views.mahsuloatlar_statistikasi, name="mahsuloatlar_statistikasi"),
    path('statistics/<str:period>/', views.statistics, name="statistics_more"),
]