from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    
    # EMPRESAS
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/nova/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),

    # EVENTOS
    path('eventos/', views.EventoListView.as_view(), name='evento_list'),
    path('eventos/<int:pk>/', views.EventoDetailView.as_view(), name='evento_detail'),

    # REUNIÕES
    path('reunioes/nova/<int:slot_id>/', views.ReuniaoCreateView.as_view(), name='reuniao_create'),
    path('reunioes/sucesso/', views.ReuniaoSuccessView.as_view(), name='reuniao_success'),

]