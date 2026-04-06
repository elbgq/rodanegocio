from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home
    path("", views.HomeView.as_view(), name="home"),

    # EMPRESAS
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/nova/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),

    # MACHING DE PERFIS
    path("empresa/<int:pk>/perfil-comprador/", views.PerfilCompradorUpdateView.as_view(), 
         name="perfil_comprador"),

    path("empresa/<int:pk>/perfil-expositor/", views.PerfilExpositorUpdateView.as_view(), 
         name="perfil_expositor"),
    
    # INTERESSES
    path("interesses/", views.InteresseListView.as_view(), name="interesse_list"),
    path("interesses/novo/", views.InteresseCreateView.as_view(), name="interesse_create"),
    path("interesses/<int:pk>/editar/", views.InteresseUpdateView.as_view(), name="interesse_update"),
    
    # REPRESENTANTES
    path("empresas/<int:empresa_id>/representantes/novo/",views.RepresentanteCreateView.as_view(),
    name="representante_novo"),
    path("representantes/<int:pk>/editar/",views.RepresentanteUpdateView.as_view(),
    name="representante_editar"),
    path("representantes/<int:pk>/excluir/", views.RepresentanteDeleteView.as_view(),
    name="representante_excluir"),
    
    # EVENTOS
    path('eventos/', views.EventoListView.as_view(), name='evento_list'),
    path('eventos/novo/', views.EventoCreateView.as_view(), name='evento_create'),
    path('eventos/<int:pk>/', views.EventoDetailView.as_view(), name='evento_detail'),
    path('eventos/<int:pk>/editar/', views.EventoUpdateView.as_view(), name='evento_update'),
    path('eventos/<int:pk>/excluir/', views.EventoDeleteView.as_view(), name='evento_delete'),
    
    # REUNIÕES
    path('evento/<int:evento_id>/reunioes/', views.reunioes_do_evento, name='reunioes_list'),
    path('evento/<int:evento_id>/reuniao/criar/', views.reuniao_criar, name='reuniao_criar'),
    path('reuniao/<int:reuniao_id>/editar/', views.reunioes_editar, name='reunioes_editar'),
    path('reuniao/<int:reuniao_id>/excluir/', views.reunioes_excluir, name='reunioes_excluir'),

    # Mesas
    path('reuniao/<int:reuniao_id>/mesas/', views.mesas_da_reuniao, name='mesas_da_reuniao'),
    path('reuniao/<int:reuniao_id>/mesas/gerar/', views.mesas_gerar, name='mesas_gerar'),

    # Reservas
    path('mesa/<int:mesa_id>/reservar/', views.mesa_reservar, name='mesa_reservar'),
    path('reserva/<int:reserva_id>/cancelar/', views.reserva_cancelar, name='reserva_cancelar'),
    path('reserva/<int:reserva_id>/editar/', views.reserva_editar, name='reserva_editar'),
    
    # Painel
    path('reuniao/<int:reuniao_id>/painel/', views.painel_da_reuniao, name='painel_reuniao'),
    
    # Acesso
    path("acesso/", views.acesso_rodanegocios, name="acesso_rodanegocios"),


]