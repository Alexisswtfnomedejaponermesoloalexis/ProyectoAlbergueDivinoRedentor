from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import CategoriaMedicamento, Medicamento, Paciente, ExpedienteMedico, SalidaMedicamento, Medico
from .forms import MedicamentoForm, PacienteForm, SalidaMedicamentoForm, HistoriaMedicaForm, MedicoForm

def index(request):
    context = {
        'criticos_count': Medicamento.objects.filter(cantidad__lt=5).count(),
        'salidas_hoy_count': SalidaMedicamento.objects.count(),
        'pacientes_count': Paciente.objects.count(),
        'medicos_count': Medico.objects.count(),
        'ultimas_salidas': SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico')[:5]
    }
    
    return render(request, 'index.html', context)
def pacientes(request):
    pacientes_list = Paciente.objects.all()
    context = {
        'pacientes': pacientes_list
    }
    return render(request, 'pacientes.html', context)

def medicos(request):
    medicos_list = Medico.objects.all()
    context = {
        'medicos': medicos_list
    }
    return render(request, 'medicos.html', context)