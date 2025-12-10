
def es_gerente_o_admin(user):
    return user.groups.filter(name__in=["Gerente", "Admin"]).exists()

def es_mesero(user):
    return user.groups.filter(name_in=["Mesero"]).exists()