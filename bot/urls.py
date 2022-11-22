from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('hook/', views.hook, name='hook'),
    path('setwebhook/', views.setwebhook, name='setwebhook'),
    path('receive', views.receive_request, name='receive')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

