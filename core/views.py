from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
)
from django.urls import reverse_lazy
from .models import (Empresa, Evento, Rodada, Representante, Mesa, Reserva,
                     Interesse, Categoria)
from .forms import (RepresentanteForm, EmpresaForm, CategoriaForm,
                    InteresseForm)
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time, date
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from core.services.matchmaking import gerar_todas_as_rodadas


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
    form_class = EmpresaForm
    template_name = 'core/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 15  # Exibe 20 por página
    ordering = ["nome"]  # Ordena por categoria e depois por nome


class EmpresaDetailView(DetailView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'core/empresa_detail.html'
    context_object_name = 'empresa'
 

class EmpresaCreateView(CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresa_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista de categorias distintas pelo nome
        categorias = Categoria.objects.filter(
            id__in=Interesse.objects.values_list("categoria", flat=True)
        ).order_by("nome")

        # Interesses agrupados por categoria
        interesses_por_categoria = {
            categoria: Interesse.objects.filter(categoria=categoria)
            for categoria in categorias
        }

        context["categorias_interesses"] = categorias
        context["interesses_por_categoria"] = interesses_por_categoria

        return context


class EmpresaUpdateView(UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresa_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista de categorias distintas pelo nome
        categorias = Categoria.objects.filter(
            id__in=Interesse.objects.values_list("categoria", flat=True)
        ).order_by("nome")

        # Interesses agrupados por categoria
        interesses_por_categoria = {
            categoria: Interesse.objects.filter(categoria=categoria)
            for categoria in categorias
        }
 
        context["categorias_interesses"] = categorias
        context["interesses_por_categoria"] = interesses_por_categoria
        
        return context

def empresa_perfil(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)

    # Agrupa os interesses da empresa por categoria
    categorias = Categoria.objects.all().prefetch_related("interesse_set")

    interesses_por_categoria = []
    for categoria in categorias:
        interesses = empresa.interesses.filter(categoria=categoria)
        if interesses.exists():
            interesses_por_categoria.append((categoria, interesses))

    context = {
        "empresa": empresa,
        "interesses_por_categoria": interesses_por_categoria,
    }

    return render(request, "core/empresa_perfil.html", context)

# -----------------------------
# INTERESSES
# -----------------------------
#===========CATEGORIA DE INTERESSE================

def categoria_list(request):
    categorias = Categoria.objects.all()
    return render(request, "core/categoria_list.html", {"categorias": categorias})

def categoria_create(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:categoria_list")
    else:
        form = CategoriaForm()

    return render(request, "core/categoria_form.html", {"form": form})

def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect("core:categoria_list")
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        "core/categoria_form.html",
        {"form": form, "categoria": categoria}
    )

def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        categoria.delete()
        return redirect("core:categoria_list")

    return render(
        request,
        "core/categoria_confirm_delete.html",
        {"categoria": categoria}
    )
    
#===========INTERESSES================
class InteresseListView(ListView):
    model = Interesse
    template_name = "core/interesse_list.html"
    context_object_name = "categorias"
    paginate_by = 10  # Exibe 10 por página
    
    def get_queryset(self):
        qs = Categoria.objects.filter(interesse__isnull=False).distinct().order_by("nome")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        categorias = context["categorias"]
        
        # Carrega interesses de cada categoria
        interesses_por_categoria = {
            categoria.id: categoria.interesse_set.order_by("nome")
            for categoria in categorias
        }

        context["interesses_por_categoria"] = interesses_por_categoria
        return context


class InteresseCreateView(CreateView):
    model = Interesse
    form_class = InteresseForm
    template_name = "core/interesse_form.html"
    success_url = reverse_lazy("core:interesse_list")


class InteresseUpdateView(UpdateView):
    model = Interesse
    form_class = InteresseForm
    template_name = "core/interesse_form.html"
    success_url = reverse_lazy("core:interesse_list")

class InteresseDeleteView(DeleteView):
    model = Interesse
    template_name = "core/interesse_confirm_delete.html"
    success_url = reverse_lazy("core:interesse_list")

    
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

def rodadas_list(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    rodadas = evento.rodadas.all().order_by("inicio_ro", "numero")

    return render(request, "core/rodadas_list.html", {
        "evento": evento,
        "rodadas": rodadas,
    })
    
# ===================================================================================
# Esta view é para gerar as rodadas automaticamente usando o algoritmo de matchmaking
# ===================================================================================
def rodadas_gerar(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == "POST":
        qtd_mesas = int(request.POST["qtd_mesas"])
        duracao = int(request.POST["duracao"])
        inicio_rodadas = request.POST["inicio_rodadas"]
        intervalo = int(request.POST["intervalo"])
        pausa_cada = int(request.POST["pausa_cada"])
        pausa_duracao = int(request.POST["pausa_duracao"])

        rodadas = gerar_todas_as_rodadas(
            evento,
            qtd_mesas,
            duracao,
            inicio_rodadas,
            intervalo,
            pausa_cada,
            pausa_duracao
        )


        return render(request, "core/rodadas_geradas.html", {
            "evento": evento,
            "rodadas": rodadas
        })

    return render(request, "core/rodadas_gerar.html", {
        "evento": evento,
        "duracoes": Rodada.DURACOES
    })
     
# ========================================================
def rodadas_do_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    rodadas = evento.rodadas.all()
    return render(request, 'core/rodadas_list.html', {
        'evento': evento,
        'rodadas': rodadas
    })


def rodadas_editar(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)

    if request.method == "POST":
        rodada.nome = request.POST["nome"]
        rodada.duracao = request.POST["duracao"]
        rodada.save()
        return redirect("core:rodadas_list", rodada.evento.id)

    return render(request, "core/rodadas_editar.html", {
        "rodada": rodada,
        "duracoes": Rodada.DURACOES
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

def mesas_da_rodada(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    mesas = rodada.mesas.all().order_by("numero")
    
    return render(request, "core/mesas_da_rodada.html", {
        "rodada": rodada,
        "mesas": mesas
    })


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
# PAINEL DE RODADAS
# -----------------------------
def painel_da_rodada(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    mesas = rodada.mesas.select_related("comprador", "expositor").all()
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

    # Mesas com vagas e mesas cheias
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

# -----------------------------
# RELATÓRIO DE AFINIDADES
# -----------------------------

def mesa_relatorio(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)

    comprador = mesa.comprador
    expositor = mesa.expositor

    interesses_comprador = set(comprador.interesses.all())
    interesses_expositor = set(expositor.interesses.all())

    afinidades = interesses_comprador.intersection(interesses_expositor)
    complementares = interesses_comprador.symmetric_difference(interesses_expositor)

    context = {
        "mesa": mesa,
        "comprador": comprador,
        "expositor": expositor,
        "afinidades": afinidades,
        "complementares": complementares,
        "interesses_comprador": interesses_comprador,
        "interesses_expositor": interesses_expositor,
    }

    return render(request, "core/mesa_relatorio.html", context)