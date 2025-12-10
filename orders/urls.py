from django.urls import path
from . import views

urlpatterns = [
    path("mesas/", views.mesas_mesero, name="mesas_mesero"),             # tomar mesa
    path("mesas/<int:mesa_id>/orden/", views.orden_mesa, name="orden_mesa"),  # orden actual
    path("mesas-atendidas/", views.mesas_atendidas, name="mesas_atendidas"),  # 👈 NUEVA
    path("mesas/<int:mesa_id>/historial/", views.historial_mesa, name="historial_mesa"),  # 👈 NUEVA
    path("orden/<int:orden_id>/estado/<str:nuevo_estado>/", views.cambiar_estado_orden, name="cambiar_estado_orden"),
]
