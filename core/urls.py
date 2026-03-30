from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    
    # EMPRESAS
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/nova/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),

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
    
    # RODADA
    path('evento/<int:evento_id>/rodadas/', views.rodadas_do_evento, name='rodadas_list'),
    path('evento/<int:evento_id>/rodadas/criar/', views.rodadas_criar, name='rodadas_criar'),
    path('rodada/<int:rodada_id>/editar/', views.rodadas_editar, name='rodadas_editar'),
    path('rodada/<int:rodada_id>/excluir/', views.rodadas_excluir, name='rodadas_excluir'),

    # Mesas
    path('rodada/<int:rodada_id>/mesas/', views.mesas_da_rodada, name='mesas_da_rodada'),
    path('rodada/<int:rodada_id>/mesas/gerar/', views.mesas_gerar, name='mesas_gerar'),
    
    # Reservas
    path('mesa/<int:mesa_id>/reservar/', views.mesa_reservar, name='mesa_reservar'),
    path('reserva/<int:reserva_id>/cancelar/', views.reserva_cancelar, name='reserva_cancelar'),
    path('reserva/<int:reserva_id>/editar/', views.reserva_editar, name='reserva_editar'),
    
    # Painel
    path('rodada/<int:rodada_id>/painel/', views.painel_da_rodada, name='painel_da_rodada'),
]