from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone
from collections import OrderedDict, defaultdict

from accounts.decorators import group_required
from .models import Mesa, Orden, OrdenItem
from .forms import OrdenItemForm

@group_required(["Mesero", "Gerente", "Admin"])
def mesas_mesero(request):
    # 1) Si el mesero escribe un número de mesa, vamos a esa mesa
    if request.method == "POST":
        numero_mesa = request.POST.get("numero_mesa")

        if numero_mesa:
            try:
                numero_mesa = int(numero_mesa)
            except ValueError:
                numero_mesa = None

        if numero_mesa is not None:
            # ⭐ OPCIÓN B: limitar a 10 mesas (1–10)
            if not (1 <= numero_mesa <= 10):
                # Si el número está fuera de rango, simplemente volvemos a la vista
                return redirect("mesas_mesero")

            # Buscar o crear la mesa con ese número
            mesa, _ = Mesa.objects.get_or_create(
                numero=numero_mesa,
                defaults={"activa": True},
            )

            # Buscar o crear una orden ABIERTA para esa mesa y ese mesero
            orden, _ = Orden.objects.get_or_create(
                mesa=mesa,
                mesero=request.user,
                estado="abierta",
            )

            return redirect("orden_mesa", mesa_id=mesa.id)

    # 2) Listar solo mesas que este mesero tiene ocupadas (orden abierta)
    usuario = request.user

    if usuario.groups.filter(name="Mesero").exists() and not usuario.is_superuser:
        mesas = (
            Mesa.objects
            .filter(ordenes__estado="abierta", ordenes__mesero=usuario)
            .distinct()
            .order_by("numero")
        )
    else:
        # Gerente/Admin ven todas las mesas con orden abierta
        mesas = (
            Mesa.objects
            .filter(ordenes__estado="abierta")
            .distinct()
            .order_by("numero")
        )

    return render(request, "orders/mesas_mesero.html", {"mesas": mesas})




@group_required(["Mesero", "Gerente", "Admin"])
def orden_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    # Buscar una orden abierta de esa mesa para ese mesero (o crearla)
    orden, creada = Orden.objects.get_or_create(
        mesa=mesa,
        mesero=request.user,
        estado="abierta",
    )

    if request.method == "POST":
        form = OrdenItemForm(request.POST)
        if form.is_valid():
            plato = form.cleaned_data["plato"]
            cantidad = form.cleaned_data["cantidad"]

            OrdenItem.objects.create(
                orden=orden,
                plato=plato,
                cantidad=cantidad,
                precio_unitario=plato.precio,
            )
            return redirect("orden_mesa", mesa_id=mesa.id)
    else:
        form = OrdenItemForm()

    contexto = {
        "mesa": mesa,
        "orden": orden,
        "items": orden.items.select_related("plato"),
        "form": form,
    }
    return render(request, "orders/orden_mesa.html", contexto)


@group_required(["Mesero", "Gerente", "Admin"])
def cambiar_estado_orden(request, orden_id, nuevo_estado):
    orden = get_object_or_404(Orden, id=orden_id)

    if request.method != "POST":
        return HttpResponseForbidden()

    usuario = request.user

    # Mesero (no superuser)
    if usuario.groups.filter(name="Mesero").exists() and not usuario.is_superuser:
        # Mesero puede:
        # - marcar PAGADA (cliente paga)
        # - marcar CANCELADA (liberar mesa, sin venta o error)
        if nuevo_estado not in ["pagada", "cancelada"]:
            return HttpResponseForbidden()

    # Gerente/Admin pueden cualquier estado válido
    if nuevo_estado not in dict(Orden.ESTADOS):
        return HttpResponseForbidden()

    # No permitir marcar como pagada una orden sin ítems
    if nuevo_estado == "pagada" and not orden.items.exists():
        return redirect("orden_mesa", mesa_id=orden.mesa.id)

    orden.cambiar_estado(nuevo_estado)

    # Después de pagar/liberar, la orden ya no estará "abierta",
    # así que la mesa se libera automáticamente (no saldrá en la lista).
    return redirect("orden_mesa", mesa_id=orden.mesa.id)

@group_required(["Gerente", "Admin"])
def ordenes_hoy(request):
    hoy = timezone.localdate()

    ordenes = (
        Orden.objects
        .select_related("mesa", "mesero")
        .filter(fecha_creacion__date=hoy)
        .order_by("-fecha_creacion")
    )

    contexto = {
        "ordenes": ordenes,
        "fecha": hoy,
    }
    return render(request, "orders/ordenes_hoy.html", contexto)


@group_required(["Mesero", "Gerente", "Admin"])
def mis_estadisticas(request):
    usuario = request.user

    # Si es gerente/admin puedes dejar que vea también las suyas, o redirigir a la vista general
    ordenes = Orden.objects.filter(mesero=usuario, estado="pagada").select_related("mesa")
    total_ganado = sum(o.total for o in ordenes)
    cantidad_ordenes = ordenes.count()

    contexto = {
        "ordenes": ordenes,
        "total_ganado": total_ganado,
        "cantidad_ordenes": cantidad_ordenes,
    }
    return render(request, "orders/mis_estadisticas.html", contexto)

@group_required(["Gerente", "Admin"])
def estadisticas_meseros(request):
    # Todas las órdenes PAGADAS
    ordenes_pagadas = (
        Orden.objects
        .filter(estado="pagada")
        .select_related("mesero", "mesa")
        .prefetch_related("items")
        .order_by("-fecha_creacion")
    )

    # Agrupamos en un diccionario por mesero
    agrupadas = defaultdict(lambda: {
        "mesero": None,
        "cantidad_ordenes": 0,
        "total_ganado": 0,
        "ordenes": [],
    })

    for orden in ordenes_pagadas:
        m = orden.mesero
        if m is None:
            continue  # por si acaso

        datos = agrupadas[m.id]
        datos["mesero"] = m
        datos["cantidad_ordenes"] += 1
        datos["total_ganado"] += orden.total  # usamos la property total
        datos["ordenes"].append(orden)

    # Convertimos a lista para el template
    estadisticas = list(agrupadas.values())

    contexto = {
        "estadisticas": estadisticas,
    }
    return render(request, "orders/estadisticas_meseros.html", contexto)


@group_required(["Mesero", "Gerente", "Admin"])
def mesas_atendidas(request):
    usuario = request.user

    if usuario.groups.filter(name="Mesero").exists() and not usuario.is_superuser:
        ordenes = (
            Orden.objects
            .filter(mesero=usuario)
            .select_related("mesa", "mesero")
            .prefetch_related("items")
            .order_by("mesa__numero", "-fecha_creacion")
        )
    else:
        ordenes = (
            Orden.objects
            .all()
            .select_related("mesa", "mesero")
            .prefetch_related("items")
            .order_by("mesa__numero", "-fecha_creacion")
        )

    mesas_dict = OrderedDict()

    for orden in ordenes:
        # 👇 si la orden no tiene ítems, la ignoramos
        if not orden.items.exists():
            continue

        mesa_id = orden.mesa.id
        if mesa_id not in mesas_dict:
            mesas_dict[mesa_id] = {
                "mesa": orden.mesa,
                "mesero": orden.mesero,
                "ultima_orden": orden,
            }

    mesas_atendidas = list(mesas_dict.values())

    contexto = {
        "mesas_atendidas": mesas_atendidas,
    }
    return render(request, "orders/mesas_atendidas.html", contexto)


@group_required(["Mesero", "Gerente", "Admin"])
def mesas_atendidas(request):
    usuario = request.user

    # Si es mesero: solo sus órdenes
    if usuario.groups.filter(name="Mesero").exists() and not usuario.is_superuser:
        ordenes = (
            Orden.objects
            .filter(mesero=usuario)
            .select_related("mesa", "mesero")
            .order_by("mesa__numero", "-fecha_creacion")
        )
    else:
        # Gerente/Admin: todas las órdenes
        ordenes = (
            Orden.objects
            .all()
            .select_related("mesa", "mesero")
            .order_by("mesa__numero", "-fecha_creacion")
        )

    # Nos quedamos con la ÚLTIMA orden por mesa (la más reciente)
    mesas_dict = OrderedDict()
    for orden in ordenes:
        mesa_id = orden.mesa.id
        if mesa_id not in mesas_dict:
            mesas_dict[mesa_id] = {
                "mesa": orden.mesa,
                "mesero": orden.mesero,
                "ultima_orden": orden,
            }

    mesas_atendidas = list(mesas_dict.values())

    contexto = {
        "mesas_atendidas": mesas_atendidas,
    }
    return render(request, "orders/mesas_atendidas.html", contexto)

@group_required(["Mesero", "Gerente", "Admin"])
def historial_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    usuario = request.user

    if usuario.groups.filter(name="Mesero").exists() and not usuario.is_superuser:
        ordenes_qs = (
            Orden.objects
            .filter(mesa=mesa, mesero=usuario)
            .select_related("mesero")
            .prefetch_related("items")
            .order_by("-fecha_creacion")
        )
    else:
        ordenes_qs = (
            Orden.objects
            .filter(mesa=mesa)
            .select_related("mesero")
            .prefetch_related("items")
            .order_by("-fecha_creacion")
        )

    # 👇 solo nos quedamos con las órdenes que tienen al menos 1 ítem
    ordenes = [o for o in ordenes_qs if o.items.exists()]

    contexto = {
        "mesa": mesa,
        "ordenes": ordenes,
    }
    return render(request, "orders/historial_mesa.html", contexto)

