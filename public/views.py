# public/views.py
from django.shortcuts import render
from menu.models import CategoriaPlato

def landing(request):
    return render(request, "public/landing.html")

from django.shortcuts import render
from django.db.models import Prefetch
from menu.models import CategoriaPlato, Plato

def carta(request):
    categoria_id = request.GET.get("categoria")

    # categorías activas
    categorias_base = CategoriaPlato.objects.filter(activo=True)

    # platos disponibles
    platos_qs = Plato.objects.filter(disponible=True)

    # si viene un id de categoría, filtramos los platos
    if categoria_id:
        platos_qs = platos_qs.filter(categoria_id=categoria_id)

    categorias = categorias_base.prefetch_related(
        Prefetch("platos", queryset=platos_qs)
    )

    contexto = {
        "categorias": categorias,
        "todas_categorias": categorias_base,           # para el <select>
        "categoria_seleccionada": int(categoria_id) if categoria_id else None,
    }
    return render(request, "public/sections/carta.html", contexto)


def quienes_somos(request):
    return render(request, "public/sections/quienes_somos.html")

def contacto(request):
    return render(request, "public/sections/contacto.html")
