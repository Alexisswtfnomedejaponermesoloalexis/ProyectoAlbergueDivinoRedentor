####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

# ESTE ES EL CEREBRO DE LA APLICACIÓN WEB, AQUÍ SE LLEVAN A ACABO TODOS LOS PROCESOS MENCIONADOS ANTERIORMENTE, DESDE DAR DE ALTA A UN PACIENTE, UNA SALIDA
# MEDICAMENTO, HASTA ELIMINAR O EDITAR SUS DATOS, DE IGUAL MANERA SE LLEVA EL CONTROL DEL EXPEDIENTE.

# TODA FUNCIÓN EXTRA QUE SE VAYA A AGREGAR A LA APLICAICÓN, DEBERÁ TENER SU FUNCIÓN EN ESTE DOCUMENTO PARA QUE ASÍ PUEDA FUNCIONAR DE MANERA ÓPTIMA.
# DEPENDIENDO DE LA FUNCIÓN QUE SE DESEE AGREGAR CAMBIARAN LOS PARÁMETROS O FUNCIONES A USAR.



####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

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


def expediente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    expediente, created = ExpedienteMedico.objects.get_or_create(paciente=paciente)
    salidas = SalidaMedicamento.objects.filter(paciente=paciente).select_related('medicamento')
    
    # Obtener todas las historias médicas ordenadas por fecha descendente
    historias = expediente.historias.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        form = HistoriaMedicaForm(request.POST)
        if form.is_valid():
            nueva_historia = form.save(commit=False)
            nueva_historia.expediente = expediente
            nueva_historia.save()
            messages.success(request, 'Nota médica agregada correctamente')
            return redirect('expediente', id=paciente.id)
    else:
        form = HistoriaMedicaForm()
    
    context = {
        'paciente': paciente,
        'expediente': expediente,
        'salidas': salidas,
        'historias': historias,
        'form': form
    }
    return render(request, 'expediente.html', context)


##FORMS 

def medicamento_nuevo(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento creado correctamente')
            return redirect('medicamentos')
    else:
        form = MedicamentoForm()
    
    context = {
        'titulo': 'Nuevo Medicamento',
        'form': form
    }
    return render(request, 'forms/medicamento_form.html', context)

def medicamento_editar(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento actualizado correctamente')
            return redirect('medicamentos')
    else:
        form = MedicamentoForm(instance=medicamento)
    
    context = {
        'titulo': 'Editar Medicamento',
        'form': form,
        'medicamento': medicamento
    }
    return render(request, 'forms/medicamento_form.html', context)

def paciente_nuevo(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente creado correctamente')
            return redirect('pacientes')
    else:
        form = PacienteForm()
    
    context = {
        'titulo': 'Nuevo Paciente',
        'form': form
    }
    return render(request, 'forms/paciente_form.html', context)

def paciente_editar(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente')
            return redirect('pacientes')
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'titulo': 'Editar Paciente',
        'form': form
    }
    return render(request, 'forms/paciente_form.html', context)

def salida_nueva(request):
    if request.method == 'POST':
        form = SalidaMedicamentoForm(request.POST)
        if form.is_valid():
            salida = form.save()
            # Actualizar inventario
            medicamento = salida.medicamento
            medicamento.cantidad -= salida.cantidad
            if medicamento.cantidad < 0:
                medicamento.cantidad = 0
            medicamento.save()
            messages.success(request, 'Salida registrada correctamente')
            return redirect('salidas')
    else:
        form = SalidaMedicamentoForm()
    
    context = {
        'titulo': 'Nueva Salida de Medicamento',
        'form': form
    }
    return render(request, 'forms/salida_form.html', context)

def medico_nuevo(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico creado correctamente')
            return redirect('medicos')
    else:
        form = MedicoForm()
    
    context = {
        'titulo': 'Nuevo Médico',
        'form': form
    }
    return render(request, 'forms/medico_form.html', context)

def medico_editar(request, id):
    medico = get_object_or_404(Medico, pk=id)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico actualizado correctamente')
            return redirect('medicos')
    else:
        form = MedicoForm(instance=medico)
    
    context = {
        'titulo': 'Editar Médico',
        'form': form,
        'medico': medico
    }
    return render(request, 'forms/medico_form.html', context)

#DELETE
def medicamento_eliminar(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado correctamente')
        return redirect('medicamentos')
    
    context = {
        'medicamento': medicamento
    }
    return render(request, 'delete/medicamento_eliminar.html', context)

def paciente_eliminar(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado correctamente')
        return redirect('pacientes')
    
    context = {
        'paciente': paciente
    }
    return render(request, 'delete/paciente_eliminar.html', context)

def medico_eliminar(request, id):
    medico = get_object_or_404(Medico, pk=id)
    
    if request.method == 'POST':
        medico.delete()
        messages.success(request, 'Médico eliminado correctamente')
        return redirect('medicos')
    
    context = {
        'medico': medico
    }
    return render(request, 'delete/medico_eliminar.html', context)

