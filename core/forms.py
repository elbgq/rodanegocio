from django import forms
from .models import Rodada, Representante

class RodadaForm(forms.ModelForm):
    data = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        localize=False
    )

    class Meta:
        model = Rodada
        fields = ["nome", "data", "duracao"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se a data veio do expediente, deixa readonly
        if self.initial.get("data"):
            self.fields["data"].widget.attrs["readonly"] = True


class RepresentanteForm(forms.ModelForm):
    class Meta:
        model = Representante
        fields = ["nome", "email", "telefone"]
