from django.urls import path
from . import views

urlpatterns = [
    path("admin-panel/", views.admin_panel, name="admin_panel"),

    path("admin-panel/platos/", views.platos_list, name="platos_list"),
    path("admin-panel/platos/nuevo/", views.plato_create, name="plato_create"),
    path("admin-panel/platos/<int:plato_id>/editar/", views.plato_update, name="plato_update"),
    path("admin-panel/platos/<int:plato_id>/eliminar/", views.plato_delete, name="plato_delete"),
]
