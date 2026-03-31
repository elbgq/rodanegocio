from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
)
from django.urls import reverse_lazy
from .models import (Empresa, Evento, Rodada,
                     Representante, Mesa)
from .forms import RodadaForm, RepresentanteForm
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time, date
from django.views import View
from django.contrib import messages

# -----------------------------
# Home
# -----------------------------
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pegamos todas as rodadas
        context['rodadas'] = Rodada.objects.all().order_by('evento__data', 'inicio_ro')
        return context

# -----------------------------
# ACESSO
# -----------------------------

SENHA_RODANEGOCIOS = "rodanegocios123"  # você define a senha aqui

def acesso_rodanegocios(request):
    if request.method == "POST":
        senha_digitada = request.POST.get("senha")

        if senha_digitada == SENHA_RODANEGOCIOS:
            request.session["acesso_rodanegocios"] = True
            return redirect("core:home")  # ajuste para sua URL real

        return render(request, "core/digite_senha.html", {
            "erro": "Senha incorreta."
        })

    return render(request, "core/digite_senha.html")

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
# REPRESENTANTE
# -----------------------------
class RepresentanteCreateView(CreateView):
    model = Representante
    form_class = RepresentanteForm
    template_name = "core/representante_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.empresa = get_object_or_404(Empresa, pk=kwargs["empresa_id"])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa"] = self.empresa
        return context

    def form_valid(self, form):
        form.instance.empresa = self.empresa
        form.save()
        return redirect("core:empresa_detail", pk=self.empresa.id)

class RepresentanteUpdateView(UpdateView):
    model = Representante
    form_class = RepresentanteForm
    template_name = "core/representante_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa"] = self.object.empresa
        return context

    def get_success_url(self):
        return reverse_lazy("core:empresa_detail", kwargs={"pk": self.object.empresa.id})

class RepresentanteDeleteView(DeleteView):
    model = Representante
    template_name = "core/representante_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("core:empresa_detail", kwargs={"pk": self.object.empresa.id})


# -----------------------------
# EVENTO
# -----------------------------
class EventoListView(ListView):
    model = Evento
    template_name = 'core/evento_list.html'
    context_object_name = 'eventos'

class EventoCreateView(CreateView):
    model = Evento
    fields = ['nome', 'data', 'local', 'inicio_ev', 'termino_ev', 'descricao']
    template_name = 'core/evento_form.html'
    success_url = reverse_lazy('core:evento_list')

class EventoDetailView(DetailView):
    model = Evento
    template_name = 'core/evento_detail.html'
    context_object_name = 'evento'

class EventoUpdateView(UpdateView):
    model = Evento
    fields = ['nome', 'data', 'local', 'inicio_ev', 'termino_ev', 'descricao']
    template_name = 'core/evento_form.html'
    success_url = reverse_lazy('core:evento_list')


class EventoDeleteView(DeleteView):
    model = Evento
    template_name = 'core/evento_confirm_delete.html'
    success_url = reverse_lazy('core:evento_list')


# -----------------------------
# RODADAS
# -----------------------------

def rodadas_do_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    rodadas = evento.rodadas.all()
    return render(request, 'core/rodadas_list.html', {
        'evento': evento,
        'rodadas': rodadas
    })

def rodadas_criar(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        duracao = int(request.POST.get('duracao'))
        inicio_str = request.POST.get('inicio_ro')
        
        # Converte para datetime
        inicio_dt = datetime.combine(evento.data, datetime.strptime(inicio_str, "%H:%M").time())
        fim_dt = inicio_dt + timedelta(minutes=duracao)

        # Converte horários do evento
        evento_inicio_dt = datetime.combine(evento.data, evento.inicio_ev)
        evento_termino_dt = datetime.combine(evento.data, evento.termino_ev)

        # Valida início
        if inicio_dt < evento_inicio_dt:
            messages.error(request, "A rodada não pode começar antes do início do evento.")
            return redirect("core:rodadas_criar", evento_id=evento.id)

        # Valida fim
        if fim_dt > evento_termino_dt:
            messages.error(request, "A rodada ultrapassa o horário final do evento.")
            return redirect("core:rodadas_criar", evento_id=evento.id)

       # Criar rodada
        Rodada.objects.create(
            evento=evento,
            nome=nome,
            duracao=duracao,
            inicio_ro=inicio_dt.time(),
            fim_ro=fim_dt.time()
        )

        messages.success(request, "Rodada criada com sucesso!")
        return redirect("core:rodadas_list", evento_id=evento.id)

    return render(request, "core/rodadas_criar.html", {
        "evento": evento,
        "duracao": Rodada.DURACOES
    })

def rodadas_editar(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    evento = rodada.evento  # para redirecionar depois

    if request.method == "POST":
        rodada.nome = request.POST.get("nome")
        rodada.duracao = request.POST.get("duracao")
        inicio_str = request.POST.get("inicio_ro")
        fim_str = request.POST.get("fim_ro")
        
        # Converte horários informados
        inicio_dt = datetime.combine(evento.data, datetime.strptime(inicio_str, "%H:%M").time())
        fim_dt = datetime.combine(evento.data, datetime.strptime(fim_str, "%H:%M").time())


        # Converte horário do evento informado
        evento_inicio_dt = datetime.combine(evento.data, evento.inicio_ev)
        evento_termino_dt = datetime.combine(evento.data, evento.termino_ev)

        
        # Valida início rodada >= início do evento
        if inicio_dt < evento_inicio_dt:
            messages.error(request, "A rodada não pode começar antes do início do evento.")
            return redirect('core:rodadas_editar', rodada_id=rodada.id)

        # Valida fim
        if fim_dt > evento_termino_dt:
            messages.error(request, "A rodada ultrapassa o horário final do evento.")
            return redirect('core:rodadas_editar', rodada_id=rodada.id)

        # Salva os horários corrigidos
        rodada.inicio_ro = inicio_dt.time()
        rodada.fim_ro = fim_dt.time()

        rodada.save()

        messages.success(request, "Rodada atualizada com sucesso!")
        return redirect('core:rodadas_list', evento_id=evento.id)

    return render(request, "core/rodadas_editar.html", {
        "rodada": rodada,
        "evento": evento
    })


def rodadas_excluir(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    evento = rodada.evento  # para redirecionar depois

    # Exclui a rodada
    rodada.delete()

    messages.success(request, "Rodada excluída com sucesso!")
    return redirect('core:rodadas_list', evento_id=evento.id)

# -----------------------------
# MESAS
# -----------------------------
#============CBV===============
'''
class MesasDaRodadaView(TemplateView):
    template_name = "core/mesas_da_rodada.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rodada_id = self.kwargs["rodada_id"]
        rodada = get_object_or_404(Rodada, id=rodada_id)

        mesas = rodada.mesas.all().order_by("numero")
        empresas = Empresa.objects.all()
        
        # empresas que já reservaram em QUALQUER mesa desta rodada
        empresas_reservadas = Reserva.objects.filter(
            mesa__rodada=rodada
        ).values_list("empresa_id", flat=True)

        # empresas já reservadas por mesa
        for mesa in mesas:
            mesa.empresas_ids = [r.empresa.id for r in mesa.reservas.all()]

        context.update({
            "rodada": rodada,
            "mesas": mesas,
            "empresas": empresas,
            "empresas_reservadas": empresas_reservadas,
        })

        return context
'''
#============FBV===============
def mesas_da_rodada(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    mesas = rodada.mesas.all().order_by("numero")
    empresas = Empresa.objects.all()
    
    # empresas que já reservaram em QUALQUER mesa desta rodada
    empresas_reservadas = Reserva.objects.filter(
        mesa__rodada=rodada).values_list('empresa_id', flat=True)
    
    # empresas já reservadas por mesa
    for mesa in mesas:
        mesa.empresas_ids = [r.empresa.id for r in mesa.reservas.all()]

    context = {
        "rodada":rodada,
        "mesas":mesas,
        "empresas":empresas,
        "empresas_reservadas":empresas_reservadas,
    }
    return render(request, "core/mesas_da_rodada.html", context)

def mesas_gerar(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)

    if request.method == "POST":
        qtd = int(request.POST.get("quantidade"))

        # Evita duplicação
        if rodada.mesas.exists():
            messages.error(request, "As mesas já foram geradas para esta rodada.")
            return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

        # Cria mesas numeradas
        for i in range(1, qtd + 1):
            Mesa.objects.create(rodada=rodada, numero=i)

        messages.success(request, f"{qtd} mesas foram geradas com sucesso!")
        return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

    return redirect('core:rodadas_list', evento_id=rodada.evento.id)



# -----------------------------
# RESERVAS
# -----------------------------
from .models import Reserva

def mesa_reservar(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    rodada = mesa.rodada

    empresa_id = request.GET.get("empresa")
    empresa = get_object_or_404(Empresa, id=empresa_id)

    # Regra 1: mesa cheia
    if mesa.reservas.count() >= 2:
        messages.error(request, "Esta mesa já está com todas as vagas preenchidas.")
        return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

    # Regra 2: empresa já reservou outra mesa nesta rodada
    if Reserva.objects.filter(mesa__rodada=mesa.rodada, empresa=empresa).exists():
        messages.error(request, "Esta empresa já possui reserva nesta rodada.")
        return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

    # Criar reserva
    Reserva.objects.create(mesa=mesa, empresa=empresa)
    messages.success(request, "Reserva realizada com sucesso!")

    return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

def reserva_cancelar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    rodada = reserva.mesa.rodada

    reserva.delete()
    messages.success(request, "Reserva cancelada com sucesso!")

    return redirect('core:mesas_da_rodada', rodada_id=rodada.id)


def reserva_editar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    mesa = reserva.mesa
    rodada = mesa.rodada
    empresas = Empresa.objects.all()

    if request.method == "POST":
        nova_empresa_id = request.POST.get("empresa")
        nova_empresa = get_object_or_404(Empresa, id=nova_empresa_id)

        # Regra: empresa já está em outra mesa
        if Reserva.objects.filter(mesa__rodada=rodada, empresa=nova_empresa).exclude(id=reserva.id).exists():
            messages.error(request, "Esta empresa já está reservada em outra mesa nesta rodada.")
            return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

        reserva.empresa = nova_empresa
        reserva.save()

        messages.success(request, "Reserva atualizada com sucesso!")
        return redirect('core:mesas_da_rodada', rodada_id=rodada.id)

    context = {
        "reserva": reserva,
        "mesa": mesa,
        "rodada": rodada,
        "empresas": empresas,
    }
    return render(request, "core/reserva_editar.html", context)
    
# -----------------------------
# PAINEL DA RODADA
# -----------------------------
def painel_da_rodada(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    mesas = rodada.mesas.all()
    empresas = Empresa.objects.all()

    total_mesas = mesas.count()
    total_reservas = Reserva.objects.filter(mesa__rodada=rodada).count()

    # Empresas que já reservaram
    empresas_reservadas_ids = Reserva.objects.filter(
        mesa__rodada=rodada
    ).values_list("empresa_id", flat=True)

    empresas_sem_reserva = empresas.exclude(id__in=empresas_reservadas_ids)

    # Ocupação
    capacidade_total = total_mesas * 2
    ocupacao_percentual = (total_reservas / capacidade_total * 100) if capacidade_total > 0 else 0

    # Mesas com vagas
    mesas_com_vagas = [m for m in mesas if m.reservas.count() < 2]
    mesas_cheias = [m for m in mesas if m.reservas.count() == 2]

    context = {
        "rodada": rodada,
        "mesas": mesas,
        "total_mesas": total_mesas,
        "total_reservas": total_reservas,
        "empresas_sem_reserva": empresas_sem_reserva,
        "ocupacao_percentual": round(ocupacao_percentual, 1),
        "mesas_com_vagas": mesas_com_vagas,
        "mesas_cheias": mesas_cheias,
    }
    return render(request, "core/painel_rodada.html", context)
