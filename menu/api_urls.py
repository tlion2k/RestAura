from django.urls import path
from . import api_views

urlpatterns = [
    # Categorías
    path("categorias/", api_views.CategoriaListAPIView.as_view(), name="api_categorias_list"),
    path("categorias/<int:pk>/", api_views.CategoriaDetailAPIView.as_view(), name="api_categorias_detail"),

    # Platos
    path("platos/", api_views.PlatoListAPIView.as_view(), name="api_platos_list"),
    path("platos/<int:pk>/", api_views.PlatoDetailAPIView.as_view(), name="api_platos_detail"),
]
