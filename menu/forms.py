from django import forms
from .models import Plato

class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ["categoria", "nombre", "descripcion", "precio", "disponible", "imagen"]

        widgets = {
            "categoria": forms.Select(attrs={
                "class": "form-select"
            }),
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Pasta al pesto"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe brevemente el plato..."
            }),
            "precio": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Ej: 8500"
            }),
            "disponible": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
