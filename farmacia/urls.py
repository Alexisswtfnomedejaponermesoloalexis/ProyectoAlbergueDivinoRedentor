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
]