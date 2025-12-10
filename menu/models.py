from django.db import models
from django.conf import settings
import os

class CategoriaPlato(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría de plato"
        verbose_name_plural = "Categorías de platos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Plato(models.Model):
    categoria = models.ForeignKey(
        "CategoriaPlato",
        on_delete=models.PROTECT,
        related_name="platos"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to="platos/", blank=True, null=True) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"
    
    @property
    def imagen_url(self):
        if self.imagen and self.imagen.name:
            return self.imagen.url
        return f"/media/comida_default.jpg"



