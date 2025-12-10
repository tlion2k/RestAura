import requests

def obtener_plato_aleatorio():
    """
    Consume una API externa (TheMealDB) para obtener un plato aleatorio.
    Devuelve un diccionario simplificado o None si falla.
    """
    url = "https://www.themealdb.com/api/json/v1/1/random.php"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        meal = data.get("meals", [None])[0]
        if not meal:
            return None

        return {
            "nombre": meal.get("strMeal"),
            "categoria": meal.get("strCategory"),
            "origen": meal.get("strArea"),
            "instrucciones": meal.get("strInstructions", "")[:300] + "...",
            "imagen": meal.get("strMealThumb"),
            "fuente": meal.get("strSource") or "https://www.themealdb.com/",
        }
    except Exception:
        # Si hay error de red o formato, no queremos romper el panel
        return None
