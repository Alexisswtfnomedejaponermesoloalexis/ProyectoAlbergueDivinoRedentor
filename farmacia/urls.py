
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

#SE CREO ESTE URLS.PY PARA CONTROLAR LAS URLS DENTRO DE LA APLICAICIÓN, EN EL OTRO URLS.PY DEL PROYECTO SE LE PUSO COMO REFERENCIA QUE TOME LAS URLS DE AQUÍ
# AQUÍ SE DESIGNA QUE TOME LAS URLS DE URLS.PY DENTRO DE LA APP DE FARMACIA
#path('', include('farmacia.urls')),  # Redirige todo a tu app


# AQUI SE DESIGNAN LAS URLS PARA NAVEGAR EN LA APLICAICÓN



####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

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

    #delete

    path('medicamentos/eliminar/<int:id>/', views.medicamento_eliminar, name='medicamento_eliminar'),
    path('pacientes/eliminar/<int:id>/', views.paciente_eliminar, name='paciente_eliminar'),
    path('medicos/eliminar/<int:id>/', views.medico_eliminar, name='medico_eliminar'),
    
]