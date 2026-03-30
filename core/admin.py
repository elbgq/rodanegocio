from django.contrib import admin
from .models import Evento, Empresa, Rodada, Representante, Mesa

# Register your models here.
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'inicio_ev', 'termino_ev')
    search_fields = ('nome',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'segmento')
    search_fields = ('nome', 'segmento')
    
@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'email')
    search_fields = ('nome', 'empresa__nome', 'email')  

@admin.register(Rodada)
class RodadaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'evento', 'duracao', 'inicio_ro', 'fim_ro')
    search_fields = ('nome', 'evento__nome')

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'rodada')
    search_fields = ('numero', 'rodada__nome')
