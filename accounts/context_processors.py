from .utils import es_gerente_o_admin

def roles_context(request):
    user = request.user
    contexto = {
        "es_gerente_o_admin": False,
        "es_mesero": False,
    }

    if user.is_authenticated:
        contexto["es_gerente_o_admin"] = es_gerente_o_admin(user)
        contexto["es_mesero"] = user.groups.filter(name="Mesero").exists()

    return contexto
