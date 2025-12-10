from django import forms
from menu.models import Plato

class OrdenItemForm(forms.Form):
    plato = forms.ModelChoiceField(
        queryset=Plato.objects.filter(disponible=True),
        widget=forms.Select(attrs={"class": "form-select"})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
