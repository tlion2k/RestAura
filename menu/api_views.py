from rest_framework import generics
from .models import CategoriaPlato, Plato
from .serializers import CategoriaPlatoSerializer, PlatoSerializer


# CATEGORÍAS

class CategoriaListAPIView(generics.ListAPIView):
    queryset = CategoriaPlato.objects.filter(activo=True)
    serializer_class = CategoriaPlatoSerializer


class CategoriaDetailAPIView(generics.RetrieveAPIView):
    queryset = CategoriaPlato.objects.filter(activo=True)
    serializer_class = CategoriaPlatoSerializer


# PLATOS

class PlatoListAPIView(generics.ListCreateAPIView):
    queryset = Plato.objects.filter(disponible=True).select_related("categoria")
    serializer_class = PlatoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get("categoria")
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset


class PlatoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plato.objects.select_related("categoria").all()
    serializer_class = PlatoSerializer
