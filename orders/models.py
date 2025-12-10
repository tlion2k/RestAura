from django.db import models
from django.contrib.auth.models import User
from menu.models import Plato

class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    mesero_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesas"
    )
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Mesa {self.numero}"


class Orden(models.Model):
    ESTADOS = [
        ("abierta", "Abierta"),
        ("servida", "Servida"),
        ("pagada", "Pagada"),
        ("cancelada", "Cancelada"),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name="ordenes")
    mesero = models.ForeignKey(User, on_delete=models.PROTECT, related_name="ordenes")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="abierta")

    def __str__(self):
        return f"Orden #{self.id} - Mesa {self.mesa.numero}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado in dict(self.ESTADOS):
            self.estado = nuevo_estado
            self.save()

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="items")
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.plato.nombre}"
