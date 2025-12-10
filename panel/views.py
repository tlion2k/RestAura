from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import group_required
from accounts.utils import es_gerente_o_admin
from menu.models import Plato
from menu.forms import PlatoForm
from menu.models import CategoriaPlato
from django.db.models import Count
import json


@login_required
def admin_panel(request):
    from menu.external_api import obtener_plato_aleatorio

    sugerencia_externa = obtener_plato_aleatorio()

    categorias = (
        CategoriaPlato.objects
        .filter(activo=True)
        .annotate(num_platos=Count("platos"))
    )

    labels = [c.nombre for c in categorias]
    data = [c.num_platos for c in categorias]

    total_categorias = CategoriaPlato.objects.filter(activo=True).count()
    total_platos = Plato.objects.count()
    platos_disponibles = Plato.objects.filter(disponible=True).count()
    platos_no_disponibles = total_platos - platos_disponibles

    contexto = {
        "sugerencia_externa": sugerencia_externa,
        "chart_labels": json.dumps(labels),
        "chart_data": json.dumps(data),
        "total_categorias": total_categorias,
        "total_platos": total_platos,
        "platos_disponibles": platos_disponibles,
        "platos_no_disponibles": platos_no_disponibles,
    }
    return render(request, "panel/dashboard.html", contexto)




@group_required(["Gerente", "Admin"])
def platos_list(request):
    platos = Plato.objects.select_related("categoria").all()
    contexto = {
        "platos": platos,
        # "es_gerente_o_admin": es_gerente_o_admin(request.user),
    }
    return render(request, "panel/platos_list.html", contexto)


@group_required(["Gerente", "Admin"])
def plato_create(request):
    if request.method == "POST":
        form = PlatoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("platos_list")
    else:
        form = PlatoForm()

    contexto = {
        "form": form,
        "accion": "Crear",
        "es_gerente_o_admin": es_gerente_o_admin(request.user),
    }
    return render(request, "panel/plato_form.html", contexto)


@group_required(["Gerente", "Admin"])
def plato_update(request, plato_id):
    plato = get_object_or_404(Plato, id=plato_id)

    if request.method == "POST":
        form = PlatoForm(request.POST, request.FILES, instance=plato)
        if form.is_valid():
            form.save()
            return redirect("platos_list")
    else:
        form = PlatoForm(instance=plato)

    contexto = {
        "form": form,
        "accion": "Editar",
        "es_gerente_o_admin": es_gerente_o_admin(request.user),
        "plato": plato,
    }
    return render(request, "panel/plato_form.html", contexto)


@group_required(["Gerente", "Admin"])
def plato_delete(request, plato_id):
    plato = get_object_or_404(Plato, id=plato_id)

    if request.method == "POST":
        plato.delete()
        return redirect("platos_list")

    contexto = {
        "plato": plato,
        "es_gerente_o_admin": es_gerente_o_admin(request.user),
    }
    return render(request, "panel/plato_confirm_delete.html", contexto)


def es_gerente_o_admin(user):
    return user.groups.filter(name__in=["Gerente", "Admin"]).exists()
