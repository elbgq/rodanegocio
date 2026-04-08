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
    path("empresa/<int:pk>/perfil/", views.empresa_perfil, name="empresa_perfil"),
    
    # CATEGORIAS
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.categoria_update, name="categoria_update"),
    path("categorias/<int:pk>/excluir/", views.categoria_delete, name="categoria_delete"),
    
    # INTERESSES
    path("interesses/", views.InteresseListView.as_view(), name="interesse_list"),
    path("interesses/novo/", views.InteresseCreateView.as_view(), name="interesse_create"),
    path("interesses/<int:pk>/editar/", views.InteresseUpdateView.as_view(), name="interesse_update"),
    path("interesses/<int:pk>/excluir/", views.InteresseDeleteView.as_view(), name="interesse_delete"),
    
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
     
    # RODADAS
    path("evento/<int:evento_id>/rodadas/gerar/", views.rodadas_gerar, name="rodadas_gerar"),
    path('evento/<int:evento_id>/rodadas/', views.rodadas_do_evento, name='rodadas_list'),
    path('rodada/<int:rodada_id>/editar/', views.rodadas_editar, name='rodadas_editar'),
    path('rodada/<int:rodada_id>/excluir/', views.rodadas_excluir, name='rodadas_excluir'),

    # Mesas
    path('rodada/<int:rodada_id>/mesas/', views.mesas_da_rodada, name='mesas_da_rodada'),
    path('rodada/<int:rodada_id>/mesas/gerar/', views.mesas_gerar, name='mesas_gerar'),
    path("mesas/<int:pk>/relatorio/", views.mesa_relatorio, name="mesa_relatorio"),
    
    # Painel
    path('rodada/<int:rodada_id>/painel/', views.painel_da_rodada, name='painel_rodada'),
    
    # Acesso
    path("acesso/", views.acesso_rodanegocios, name="acesso_rodanegocios"),

]