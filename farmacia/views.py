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

def medicamentos(request):
    medicamentos_list = Medicamento.objects.select_related('categoria').all()
    criticos = Medicamento.objects.filter(cantidad__lt=5)
    categorias = CategoriaMedicamento.objects.all()
    
    context = {
        'medicamentos': medicamentos_list,
        'criticos': criticos,
        'categorias': categorias
    }
    return render(request, 'medicamentos.html', context)

def salidas(request):
    salidas_list = SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico').all()
    context = {
        'salidas': salidas_list
    }
    return render(request, 'salidas.html', context)

def reportes(request):
    # Estadísticas de medicamentos más entregados
    medicamentos_mas_entregados = SalidaMedicamento.objects.values(
        'medicamento__nombre'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    # Medicamentos críticos
    medicamentos_criticos = Medicamento.objects.filter(cantidad__lt=5)
    
    context = {
        'medicamentos_mas_entregados': medicamentos_mas_entregados,
        'medicamentos_criticos': medicamentos_criticos
    }
    return render(request, 'reportes.html', context)

def reportes(request):
    # Estadísticas de medicamentos más entregados
    medicamentos_mas_entregados = SalidaMedicamento.objects.values(
        'medicamento__nombre'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    # Medicamentos críticos
    medicamentos_criticos = Medicamento.objects.filter(cantidad__lt=5)
    
    context = {
        'medicamentos_mas_entregados': medicamentos_mas_entregados,
        'medicamentos_criticos': medicamentos_criticos
    }
    return render(request, 'reportes.html', context)