from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pacientes/', views.pacientes, name='pacientes'),
    path('medicos/', views.medicos, name='medicos'),
    path('medicamentos/', views.medicamentos, name='medicamentos'),
    path('salidas/', views.salidas, name='salidas'),
    path('expediente/<int:id>/', views.expediente, name='expediente'),
    path('reportes/', views.reportes, name='reportes'),

    #forms

    path('medicamentos/nuevo/', views.medicamento_nuevo, name='medicamento_nuevo'),
    path('medicamentos/editar/<int:id>/', views.medicamento_editar, name='medicamento_editar'),
    path('salidas/nueva/', views.salida_nueva, name='salida_nueva'),
    path('pacientes/nuevo/', views.paciente_nuevo, name='paciente_nuevo'),
    path('pacientes/editar/<int:id>/', views.paciente_editar, name='paciente_editar'),
    path('medicos/nuevo/', views.medico_nuevo, name='medico_nuevo'),
    path('medicos/editar/<int:id>/', views.medico_editar, name='medico_editar'),
]