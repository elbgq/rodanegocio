from django.shortcuts import render, get_object_or_404

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView
)
from django.urls import reverse_lazy
from .models import Empresa, Evento, SlotHorario, Reuniao

from django.views.generic import TemplateView

# -----------------------------
# Home
# -----------------------------
class HomeView(TemplateView):
    template_name = 'core/home.html'
    
# -----------------------------
# EMPRESA
# -----------------------------
class EmpresaListView(ListView):
    model = Empresa
    template_name = 'core/empresa_list.html'
    context_object_name = 'empresas'


class EmpresaDetailView(DetailView):
    model = Empresa
    template_name = 'core/empresa_detail.html'
    context_object_name = 'empresa'


class EmpresaCreateView(CreateView):
    model = Empresa
    fields = ['nome', 'descricao', 'site', 'segmento']
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresa_list')


class EmpresaUpdateView(UpdateView):
    model = Empresa
    fields = ['nome', 'descricao', 'site', 'segmento']
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresa_list')


# -----------------------------
# EVENTO
# -----------------------------
class EventoListView(ListView):
    model = Evento
    template_name = 'core/evento_list.html'
    context_object_name = 'eventos'


class EventoDetailView(DetailView):
    model = Evento
    template_name = 'core/evento_detail.html'
    context_object_name = 'evento'


# -----------------------------
# REUNIÃO
# -----------------------------
class ReuniaoCreateView(CreateView):
    model = Reuniao
    fields = ['empresa_a', 'empresa_b']
    template_name = 'core/reuniao_form.html'

    def form_valid(self, form):
        slot_id = self.kwargs['slot_id']
        form.instance.slot = get_object_or_404(SlotHorario, id=slot_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reuniao_success')


class ReuniaoSuccessView(TemplateView):
    template_name = 'core/reuniao_success.html'
