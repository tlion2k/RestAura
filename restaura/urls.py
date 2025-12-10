from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Público
    path("", include("public.urls")),

    # Auth
    path("", include("accounts.urls")),

    # Panel
    path("", include("panel.urls")),

    # API REST
    path("api/", include("menu.api_urls")),

    # Mesero / Ordenes
    path("orders/", include("orders.urls")),
]

handler403 = "accounts.views.error_403"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)