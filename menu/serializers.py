from rest_framework import serializers
from .models import CategoriaPlato, Plato

class CategoriaPlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPlato
        fields = ["id", "nombre", "descripcion", "activo"]


class PlatoSerializer(serializers.ModelSerializer):
    categoria = CategoriaPlatoSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria",
        queryset=CategoriaPlato.objects.all(),
        write_only=True
    )

    class Meta:
        model = Plato
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "disponible",
            "fecha_creacion",
            "categoria",
            "categoria_id",
        ]
