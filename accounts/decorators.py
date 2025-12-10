from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render   # 👈 agrega render
from functools import wraps

def group_required(groups):
    if isinstance(groups, str):
        groups = [groups]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):

            # Si no está logueado → al login
            if not request.user.is_authenticated:
                return redirect("/login/")

            print("Grupos permitidos:", groups)
            print("Usuario:", request.user.username)
            print("Usuario grupos:", list(request.user.groups.values_list("name", flat=True)))

            # Si está en alguno de los grupos permitidos → pasa
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)

            # Si está logueado pero NO tiene permiso → devolver 403 con tu template
            return render(request, "403.html", status=403)

        return _wrapped
    return decorator
