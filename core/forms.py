from django import forms
from .models import (Reuniao, Representante, PerfilComprador,
                     PerfilExpositor, Empresa, Interesse)
import re

from django import forms
from .models import Empresa

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = "__all__"
        widgets = {
            "interesses": forms.CheckboxSelectMultiple(),  # ou forms.SelectMultiple()
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona classes Bootstrap automaticamente
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ["CheckboxSelectMultiple"]:
                field.widget.attrs.update({"class": "form-control"})

    def clean_site(self):
        site = self.cleaned_data.get("site")
        if site and not site.startswith(("http://", "https://")):
            site = "https://" + site
        return site

class PerfilCompradorForm(forms.ModelForm):
    class Meta:
        model = PerfilComprador
        fields = "__all__"
        widgets = {
            "paises_que_trabalha": forms.CheckboxSelectMultiple(),
            "preco_medio": forms.CheckboxSelectMultiple(),
            "tipos_produto": forms.CheckboxSelectMultiple(),
            "regioes_interesse": forms.CheckboxSelectMultiple(),
        }

class PerfilExpositorForm(forms.ModelForm):
    class Meta:
        model = PerfilExpositor
        fields = "__all__"
        widgets = {
            "preco_faixa": forms.CheckboxSelectMultiple(),
            "tipos_produto": forms.CheckboxSelectMultiple(),
            "regioes_brasil": forms.CheckboxSelectMultiple(),
            "perfil_comprador_desejado": forms.CheckboxSelectMultiple(),
        }
        
class InteresseForm(forms.ModelForm):
    class Meta:
        model = Interesse
        fields = ["categoria", "nome"]
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "nome": forms.TextInput(attrs={"class": "form-control"}),
        }
    
    
class ReuniaoForm(forms.ModelForm):
    data = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        localize=False
    )

    class Meta:
        model = Reuniao
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
        
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and not forms.EmailField().clean(email):
            raise forms.ValidationError("Informe um e-mail válido.")

        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        # Aceita formatos como:
        # 999999999
        # (99) 9999-9999
        # (99) 99999-9999
        # 99 99999-9999
        padrao = r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$'

        if telefone and not re.match(padrao, telefone):
            raise forms.ValidationError("Informe um telefone válido. Ex: (11) 98765-4321")

        return telefone
