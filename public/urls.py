# public/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.landing, name="landing"),
    path("carta/", views.carta, name="carta"),
    path("quienes-somos/", views.quienes_somos, name="quienes_somos"),
    path("contacto/", views.contacto, name="contacto"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)